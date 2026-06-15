"""
ASGI config for umsproj project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import umsapp.routing  # your websocket routes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umsproj.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # regular HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            umsapp.routing.websocket_urlpatterns  # WebSocket routes for real-time pending attendance
        )
    ),
})