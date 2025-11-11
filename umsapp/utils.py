from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_session(session_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"session_{session_id}",
        {"type": "session_update", "data": data}
    )
