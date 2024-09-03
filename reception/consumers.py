import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Vérifier si l'utilisateur est authentifié
        if self.scope['user'].is_authenticated:
            self.group_name = 'chat'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

            # Charger les messages dans un contexte asynchrone
            messages = await self.get_messages()
            for message in messages:
                await self.send(text_data=json.dumps({
                    'message': f'{message["user__username"]}: {message["content"]}'
                }))
        else:
            # Refuser la connexion si l'utilisateur n'est pas connecté
            await self.close()

    async def disconnect(self, close_code):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if self.scope['user'].is_authenticated:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            user = self.scope['user']
            if user.is_authenticated:
                await self.save_message(user, message)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message  # Envoyer seulement le contenu
                }
            )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_messages(self):
        return list(
            Message.objects.order_by('-timestamp').values('user__username', 'content')[:50]
        )

    @database_sync_to_async
    def save_message(self, user, content):
        return Message.objects.create(user=user, content=content)
