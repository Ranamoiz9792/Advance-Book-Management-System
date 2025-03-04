from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BookViewSet


router = DefaultRouter()
router.register('bookdetail', BookViewSet, basename='bookdetail')

urlpatterns =[

    path('', include(router.urls)),
    path('bookdetail/<int:pk>/read/', BookViewSet.as_view({'get': 'read_book'}), name='read-book'),
    path('bookdetail/like_book/', BookViewSet.as_view({'post': 'like_book'}), name='like-book'),
]
