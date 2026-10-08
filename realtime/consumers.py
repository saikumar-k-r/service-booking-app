import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .events import (
    BOOKING_STATUS_CHANGED,
    HEARTBEAT,
    HEARTBEAT_ACK,
    PRESENCE_CHANGED,
    build_event,
)
from .models import DevicePresence


class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")
        self.device_id = self.scope.get("device_id")

        if not self.user or self.user.is_anonymous:
            await self.close(code=4401)
            return

        if not self.device_id:
            await self.close(code=4400)
            return

        self.group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.update_presence(True)

        await self.accept()

        await self.send_event(
            PRESENCE_CHANGED,
            {
                "user_id": self.user.id,
                "device_id": self.device_id,
                "online": True,
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

        if (
            hasattr(self, "user")
            and self.user
            and not self.user.is_anonymous
            and hasattr(self, "device_id")
            and self.device_id
        ):
            await self.update_presence(False)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_event(
                "error",
                {"message": "Invalid JSON"},
            )
            return

        if data.get("event") == HEARTBEAT:
            await self.update_presence(True)

            await self.send_event(
                HEARTBEAT_ACK,
                {
                    "device_id": self.device_id,
                    "server_time": timezone.now().isoformat(),
                },
            )

    async def send_event(self, event_name, payload):
        await self.send(
            text_data=json.dumps(
                build_event(event_name, payload)
            )
        )

    async def realtime_event(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event_id": event["event_id"],
                    "event": event["event"],
                    "payload": event["payload"],
                }
            )
        )

    @database_sync_to_async
    def update_presence(self, online):
        presence, _ = DevicePresence.objects.get_or_create(
            user=self.user,
            device_id=self.device_id,
        )

        presence.is_online = online
        presence.last_seen = timezone.now()

        if online:
            presence.connected_at = timezone.now()

        presence.save()

        return presence