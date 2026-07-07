# notifications/services/push_service.py
from notifications.models import Notification, DeviceToken


class PushService:

    @staticmethod
    def send(notification_id):
        from notifications.firebase import FIREBASE_AVAILABLE

        if not FIREBASE_AVAILABLE:
            print("Firebase not available — skipping push notification")
            return

        from firebase_admin import messaging

        try:
            notification = Notification.objects.select_related(
                "recipient"
            ).get(id=notification_id)
        except Notification.DoesNotExist:
            print(f"Notification {notification_id} not found")
            return

        devices = DeviceToken.objects.filter(
            user=notification.recipient,
            is_active=True,
        )

        if not devices.exists():
            return

        failed_devices = []

        for device in devices:
            message = messaging.Message(
                token=device.token,
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body,
                ),
                data={
                    "notification_id": str(notification.id),
                    "type": notification.type,
                },
            )

            try:
                response = messaging.send(message)
                print(f"Push sent successfully: {response}")

            except messaging.UnregisteredError:
                # token is no longer valid — deactivate it
                device.is_active = False
                device.save()
                failed_devices.append(device.token)
                print(f"Device token unregistered, deactivated: {device.token[:20]}")

            except messaging.SenderIdMismatchError:
                device.is_active = False
                device.save()
                failed_devices.append(device.token)
                print(f"Sender ID mismatch, deactivated: {device.token[:20]}")

            except Exception as e:
                print(f"Failed to send push to {device.token[:20]}: {e}")

        if failed_devices:
            print(f"Total failed devices: {len(failed_devices)}")