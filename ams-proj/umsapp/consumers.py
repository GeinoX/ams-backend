# umsapp/consumers.py
import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


class PendingAttendanceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.teacher_id = self.scope['url_route']['kwargs']['teacher_id']
        self.group_name = f"session_{self.session_id}_teacher_{self.teacher_id}"

        # ── JWT auth ─────────────────────────────────────────────────────
        # Token must be passed as a query param: ?token=<access_token>
        query_string = self.scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token_list = params.get('token', [])

        if not token_list:
            await self.close(code=4001)
            return

        token_str = token_list[0]
        user = await self._get_user_from_token(token_str)

        if user is None:
            await self.close(code=4001)
            return

        # ── Verify caller is actually a teacher ──────────────────────────
        is_teacher = await self._is_teacher(user)
        if not is_teacher:
            await self.close(code=4003)
            return

        self.scope['user'] = user

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_pending_student(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    # ── Helpers ──────────────────────────────────────────────────────────

    @database_sync_to_async
    def _get_user_from_token(self, token_str):
        try:
            access_token = AccessToken(token_str)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
            return None

    @database_sync_to_async
    def _is_teacher(self, user):
        return hasattr(user, 'teacher_profile')