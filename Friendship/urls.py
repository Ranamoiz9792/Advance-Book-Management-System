from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (

    FriendRequestViewSet, FriendshipViewSet, MessageViewSet
)

router = DefaultRouter()

router.register(r'friend_request', FriendRequestViewSet, basename='friend-request')
router.register(r'friends', FriendshipViewSet, basename='friends')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
