# Real-Time Event Contract

## WebSocket

ws://127.0.0.1:8000/ws/realtime/?token=<ACCESS_TOKEN>&device_id=<DEVICE_ID>

## Authentication

JWT access token is supplied through the WebSocket query parameter.

## Events

### presence.changed

```json
{
  "event": "presence.changed",
  "payload": {
    "user_id": 1,
    "device_id": "android-001",
    "online": true
  }
}