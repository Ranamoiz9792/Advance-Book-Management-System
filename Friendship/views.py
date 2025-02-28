from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import FriendRequest, Friendship, Message
from .serializer import FriendRequestSerializer, FriendshipSerializer, MessageSerializer
from CustomUsers.models import User  # Import your custom User model
from AdvanceBookManagement.utils import JWTAuthentication

class FriendRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        sender = request.user
        receiver_id = request.data.get("receiver_id")
        receiver = get_object_or_404(User, id=receiver_id)

        if sender == receiver:
            return Response({"details": "You cannot send a friend request to yourself."},
                             status=status.HTTP_400_BAD_REQUEST)

        if Friendship.objects.filter(user1=sender,
                                    user2=receiver).exists() or Friendship.objects.filter(user1=receiver,
                                     user2=sender).exists():
            return Response({"details": "You are already friends."},
                             status=status.HTTP_400_BAD_REQUEST)

        friend_request, created = FriendRequest.objects.get_or_create(sender=sender,
                                                                       receiver=receiver)
        if not created:
            return Response({"details": "Friend request already sent."}
                            , status=status.HTTP_400_BAD_REQUEST)

        return Response({"details": "Friend request sent."},
                         status=status.HTTP_201_CREATED)

    def list(self, request):

        user = request.user
        requests = FriendRequest.objects.filter(receiver=user, status="pending")
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):

        friend_request = get_object_or_404(FriendRequest, id=pk, receiver=request.user)
        action = request.data.get("action")

        if action == "accept":
            Friendship.objects.create(user1=friend_request.sender, user2=friend_request.receiver)
            friend_request.status = "accepted"
        elif action == "reject":
            friend_request.status = "rejected"
        else:
            return Response({"details": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.save()
        return Response({"details": f"Friend request {action}ed."}, status=status.HTTP_200_OK)


class FriendshipViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        user = request.user
        friends = Friendship.objects.filter(user1=user) | Friendship.objects.filter(user1=user)
        serializer = FriendshipSerializer(friends, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        sender = request.user
        receiver_id = request.data.get("receiver_id")
        content = request.data.get("content")
        receiver = get_object_or_404(User, id=receiver_id)

        if not (Friendship.objects.filter(user1=sender, user2=receiver).exists() or 
                Friendship.objects.filter(user1=receiver, user2=sender).exists()):
            return Response({"details": "You can only message friends."}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(sender=sender, receiver=receiver, content=content)
        return Response({"details": "Message sent."}, status=status.HTTP_201_CREATED)

    def list(self, request):
        user = request.user
        messages = Message.objects.filter(receiver=user).order_by('-timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
