"""
ASGI config for AdvanceBookManagement project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from PublishBooks.counsumer import NotificationConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AdvanceBookManagement.settings')
django_asgi_app = get_asgi_application()



ws_urlpatterns = [
    re_path(r'ws/book/(?P<user_id>\d+)/$', NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(URLRouter(ws_urlpatterns)),
    "http": django_asgi_app,
    
})