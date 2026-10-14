import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Connected")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "invalid JSON"}))
            return
        message = str(data.get("message", ""))
        await self.send(text_data=json.dumps({"echo": message.upper()}))

    async def disconnect(self, close_code):
        print("Disconnected:", close_code)
