import json
from channels.generic.websocket import AsyncWebsocketConsumer

online_users = set()  # Храним список активных пользователей

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            online_users.add(user.id)
            await self.channel_layer.group_add("online_users", self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated and user.id in online_users:
            online_users.remove(user.id)

        await self.channel_layer.group_discard("online_users", self.channel_name)

    async def receive(self, text_data):
        pass  # Можно добавить логику, если нужно получать сообщения
