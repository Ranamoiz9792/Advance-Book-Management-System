from django.contrib.auth.hashers import make_password, check_password
from django_redis import get_redis_connection  # Use Redis instead of Django's cache
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from AdvanceBookManagement.utils import JWTAuthentication
from .models import User
from PublishBooks.models import Book
from .serializer import SignupSerializer, LoginSerializer
from .utils import generate_otp, send_email, generate_email_body, generate_jwt_token


class SignupViewSet(viewsets.ViewSet):
    
    def create(self, request):
        """Handles signup request, stores data in Redis cache, and sends OTP."""
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        name = serializer.validated_data['name']
        password = serializer.validated_data['password']
        phone_number = serializer.validated_data['phone_number']

        if User.objects.filter(email=email).exists():
            return Response({"details": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"details": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP and store user data in Redis cache (valid for 10 mins)
        otp = str(generate_otp())
        redis_conn = get_redis_connection("default")
        redis_conn.hmset(f"user:{email}", {"username": username, "email": email, "password": password, "name": name, "phone_number": phone_number, "otp": otp})
        redis_conn.expire(f"user:{email}", 600)  # Expire after 10 mins

        # Send OTP via email
        email_body = generate_email_body(otp)
        email_sent = send_email(email, "Login Verification Code", email_body)

        if not email_sent:
            return Response({"details": "Failed to send OTP, please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"details": "OTP sent to email"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        """Handles OTP verification and saves user if OTP is correct."""
        email = request.data.get('email')
        otp = request.data.get('otp')

        redis_conn = get_redis_connection("default")
        cached_data = redis_conn.hgetall(f"user:{email}")

        if not cached_data:
            return Response({"details": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Convert Redis data from bytes to string
        cached_data = {k.decode(): v.decode() for k, v in cached_data.items()}

        if cached_data['otp'] != otp:
            return Response({"details": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Save user to database
        hashed_password = make_password(cached_data['password'])
        user = User.objects.create(
            username=cached_data['username'],
            email=cached_data['email'],
            name=cached_data['name'],
            phone_number=cached_data['phone_number'],
            password=hashed_password
        )

        # Remove data from Redis after successful signup
        redis_conn.delete(f"user:{email}")

        return Response({"details": "User created successfully", "username": user.username}, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.ViewSet):
    
    def create(self, request):
        """Handles login request."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Authenticate user
        user =User.objects.filter(email=email).first()
        if user is None:
            return Response({"details": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        if check_password(password, user.password):
            token = generate_jwt_token(user.email)
            return Response({"details": "Login successful", "token": token}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        

class ProfileViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        user = request.user
        total_likes = Book.objects.filter(published_by=user).aggregate(total_likes=Count('likes'))['total_likes'] or 0
        books = Book.objects.filter(published_by=user).values('id', 'title', 'cover_image', 'pdf_content')

        data = {
            "name": user.name,
            "profile_photo": request.build_absolute_uri(user.profile_image.url) if user.profile_image else None,
            "total_likes_received": total_likes,
            "books_shared": books.count(),
            "books_published": list(books)
        }
        return Response(data)
