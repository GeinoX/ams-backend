"""
ASGI config for umsproj project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from notificationapp import routing as notif_routing
from notificationapp.middleware import JwtAuthMiddleware  # your custom middleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(   # use your JWT middleware here
        URLRouter(
            notif_routing.websocket_urlpatterns
        )
    ),
})
