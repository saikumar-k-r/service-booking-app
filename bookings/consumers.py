import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BookingStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.booking_id = self.scope["url_route"]["kwargs"]["booking_id"]

        await self.accept()

        await self.send(text_data=json.dumps({
            "message": "Connected to booking WebSocket",
            "booking_id": self.booking_id
        }))

    async def receive(self, text_data):
      import json

      data = json.loads(text_data)

      status = data.get("status")

      await self.send(text_data=json.dumps({
        "booking_id": self.booking_id,
        "status": status,
        "message": "Booking status received successfully."
    }))

    async def disconnect(self, close_code):
        print(f"Booking WebSocket disconnected: {close_code}")