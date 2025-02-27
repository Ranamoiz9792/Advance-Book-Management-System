from AdvanceBookManagement.utils import JWTAuthentication
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from asgiref.sync import async_to_sync
from .models import Book,Like
from .serializer import BookSerializer
from channels.layers import get_channel_layer
class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def create(self, request):
        data=request.data
        user = request.user
        serializer = BookSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "message" : "Data not valid",
                "errors" : serializer.errors,   
            })
        serializer.save(
            published_by=user
        )
        return Response({
            "message" : "Data Saved Successfully",
            "data" : serializer.data,
        })
    
    def list(self, request):
        try:
            books = Book.objects.all()
            if books:
                return Response({
                    "message" : "Books Found",
                    "Books" : [
                        {
                         'id': book.id,
                         'title': book.title,
                         'description':book.description,
                        'author': book.author,
                        'published_by': book.published_by.username,
                        'cover_image': book.cover_image.url,
                        'created_at' : book.created_at,

                    }
                    for book in books
                ]
                })
            
        except Book.DoesNotExist:
            return Response({
                "message" : "No books found",
            })
        
    def retrieve(self, request, pk=None):
        book = get_object_or_404(Book, id=pk)
        serializer = BookSerializer(book,
             context={'request': request})
        return Response({"data": serializer.data},
                status=status.HTTP_200_OK)
    
    def partial_update(self, request, pk=None):
        try:
            book = Book.objects.get(id=pk)
            data = request.data
            serializer = BookSerializer(book, data=data, partial=True)
            if not serializer.is_valid():
                return Response({
                    "message" : "Data not valid",
                    "errors" : serializer.errors,   
                })
            serializer.save()
            return Response({
                "message" : "Data Saved Successfully",
                "data" : serializer.data,
            })
        except Book.DoesNotExist:
            return Response({
                "message" : "Book not found",
            })
    def destroy(self, request, pk=None):
        try:
            book = Book.objects.get(id=pk)
            book.delete()
            return Response({
                "message": "Book deleted successfully",
                "data": {}
            }, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({
                "message": "Book not found",
            }, status=status.HTTP_404_NOT_FOUND)
    
    def read_book(self, request, pk=None):
        """explain what this is doing"""
        # get the book
        book = get_object_or_404(Book, id=pk)
        # check if the book has a pdf file
        if not book.pdf_content:
            return Response({"message": "PDF file not available for this book."}, status=status.HTTP_404_NOT_FOUND)
        # return the pdf file, rb stands for read binary file, application/pdf for browser to recgonize it as pdf
        return FileResponse(book.pdf_content.open('rb'), content_type='application/pdf')
    
    @action(detail=False, methods=['post'], url_path='like_book')
    def like_book(self, request):
        user = request.user
        book_id = request.data.get("book_id")

        if not book_id:
            return Response({'message': 'Please provide book ID'},
                             status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, id=book_id)
        

        like, created = Like.objects.get_or_create(user=user, book=book)

        if not created:
            return Response({'message': 'Book already liked'},
                             status=status.HTTP_200_OK)
        
        
        self.notify_publisher(book,user)
        print()

        return Response({'message': 'Book liked successfully',
                          'total_likes': book.total_likes()},
                            status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='book_likes')
    def book_likes(self, request, pk=None):
        book = get_object_or_404(Book, pk=pk)
        
        total_likes = book.likes.count()
        liked_users = book.likes.values_list('user__username', flat=True)

        return Response({
            'total_likes': total_likes,
            'liked_users': liked_users
        }, status=status.HTTP_200_OK)
    
    def notify_publisher(self, book, user):
    # Get the channel layer
        channel_layer = get_channel_layer()
        print(f"Sending notification to publisher {book.published_by.id} by {book.published_by.username}")
        print(f"Message: User {user.username} liked your book: {book.title}")

        # Send a message to the publisher's WebSocket group
        async_to_sync(channel_layer.group_send)(
            f"notifications_{book.published_by.id}",  # Group name for the publisher
            {
                "type": "send_notification",
                "message": f"User {user.username} liked your book: {book.title}",
            },
        )
