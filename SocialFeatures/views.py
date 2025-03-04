from AdvanceBookManagement.utils import JWTAuthentication
from rest_framework import  status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Book, Comment
from .serializer import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    def create(self, request):
        
        data = request.data
        book_id = data.get('book_id')
        if not book_id:
            return Response({"message": "Book ID is required"},
             status=status.HTTP_400_BAD_REQUEST)

        book = Book.objects.filter(id=book_id).first()
        if not book:
            return Response({"message": "Book not found"},
             status=status.HTTP_404_NOT_FOUND)

        if book.published_by == request.user:
            return Response({"message": "You cannot comment on your own book."},
             status=status.HTTP_401_UNAUTHORIZED)

        serializer = CommentSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "message": "Data not valid",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(book=book, user=request.user)

        return Response({
            "message": "Comment added successfully",
            "data": serializer.data,
        }, status=status.HTTP_201_CREATED)
    

    def partial_update(self, request, pk=None):
        comment = Comment.objects.filter(id=pk)
        if not comment:
            return Response({"message": "Comment not found"},
             status=status.HTTP_404_NOT_FOUND)
        if comment.first().user!= request.user:
            return Response({"message": "You cannot update this comment."},
             status=status.HTTP_401_UNAUTHORIZED)
        serializer = CommentSerializer(comment.first(),
         data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "message": "Data not valid",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response({
            "message": "Comment updated successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        comment = Comment.objects.filter(id=pk)
        if not comment:
            return Response({"message": "Comment not found"},
             status=status.HTTP_404_NOT_FOUND)
        if comment.first().user!= request.user:
            return Response({"message": "You cannot delete this comment."},
             status=status.HTTP_401_UNAUTHORIZED)
        comment.delete()

        return Response({
            "message": "Comment deleted successfully",
            "data": {},
        }, status=status.HTTP_200_OK)


