import jwt
from urllib.parse import parse_qs
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token_list = parse_qs(query_string).get("token")
        scope["user"] = AnonymousUser()

        if token_list:
            token = token_list[0]
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                user = await get_user(user_id)
                if user:
                    scope["user"] = user
            except Exception as e:
                print(f"❌ Invalid token: {e}")

        return await super().__call__(scope, receive, send)
        