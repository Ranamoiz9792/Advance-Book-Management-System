from rest_framework import serializers

from .models import Book

class BookSerializer(serializers.ModelSerializer):
    total_likes = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    liked_users = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description', 'published_by', 'cover_image','pdf_content', 'created_at','total_likes', 'is_liked', 'liked_users']
        read_only_fields = ['published_by']

    def get_is_liked(self, obj):
        request = self.context.get('request') 
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_total_likes(self, obj):
        return obj.likes.count()
    
 
