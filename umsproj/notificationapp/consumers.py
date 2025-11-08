import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from .models import Notification
from umsapp.models import Enrollment

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Async-safe WebSocket consumer for notifications.
    All DB access wrapped in @database_sync_to_async.
    """

    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        # Accept the connection
        await self.accept()

        # Subscribe this consumer to the user's personal Redis group
        await self.channel_layer.group_add(
            f"user_{self.user.id}",
            self.channel_name
        )

        # Fetch undelivered notifications
        undelivered = await self.get_undelivered_notifications()
        for notif in undelivered:
            await self.send(text_data=json.dumps({
                "message": notif["message"],
                "timestamp": str(notif["timestamp"]),
                "sender": notif["sender_name"]
            }))
            await self.mark_delivered_by_id(notif["id"])

    async def disconnect(self, close_code):
        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Receive messages from teacher:
        {
            "message": "Exam tomorrow",
            "course_id": 5
        }
        """
        data = json.loads(text_data)
        message = data.get("message")
        course_id = data.get("course_id")
        sender = self.user

        if not message or not course_id:
            return  # ignore invalid messages

        # Fetch students of the course
        recipients = await self.get_users_by_course(course_id)

        # Create notification in DB
        notif = await self.create_notification(sender, recipients, message)

        # Send via channel layer to all recipients
        channel_layer = get_channel_layer()
        for recipient in recipients:
            await channel_layer.group_send(
                f"user_{recipient.id}",
                {
                    "type": "send_notification",
                    "message": message,
                    "sender": sender.name,
                    "timestamp": str(notif["timestamp"]),
                    "course": course_id
                }
            )

        # Mark delivered for connected users
        for recipient in recipients:
            await self.mark_delivered_by_id(notif["id"], recipient)

    async def send_notification(self, event):
        """
        Called by channel layer to send message to WebSocket.
        """
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "course": event["course"]
        }))

    # ---------------- DB helpers ---------------- #

    @database_sync_to_async
    def create_notification(self, sender, recipients, message):
        notif = Notification.objects.create(sender=sender, message=message)
        notif.recipients.set(recipients)
        # Return plain dict to avoid lazy ORM access in async
        return {
            "id": notif.id,
            "message": notif.message,
            "timestamp": notif.timestamp,
            "sender_name": notif.sender.name
        }

    @database_sync_to_async
    def get_users_by_course(self, course_id):
        # Fetch students and prefetch related user objects
        enrollments = list(Enrollment.objects.filter(course_id=course_id).select_related("student__user"))
        return [enrollment.student.user for enrollment in enrollments]

    @database_sync_to_async
    def get_undelivered_notifications(self):
        notifications = Notification.objects.filter(recipients=self.user).exclude(delivered=self.user).select_related("sender")
        result = []
        for notif in notifications:
            result.append({
                "id": notif.id,
                "message": notif.message,
                "timestamp": notif.timestamp,
                "sender_name": notif.sender.name
            })
        return result

    @database_sync_to_async
    def mark_delivered_by_id(self, notif_id, user=None):
        if user is None:
            user = self.user
        notif = Notification.objects.get(id=notif_id)
        notif.delivered.add(user)
