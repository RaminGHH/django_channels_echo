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


class ChatConsumer(AsyncWebsocketConsumer):
    group_name = "chat"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "invalid JSON"}))
            return

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.message", "message": str(data.get("message", ""))},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))