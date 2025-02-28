from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SignupViewSet, LoginViewSet
from .views import ProfileViewSet

router = DefaultRouter()
router.register(r'signup', SignupViewSet, basename='signup')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
