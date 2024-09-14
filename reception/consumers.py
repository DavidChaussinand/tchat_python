import json
from django.contrib.auth.models import User  # Importer le modèle User
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
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

            # Charger les messages du chat général (sans destinataire)
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
                # Sauvegarder le message dans le chat général (recipient=None)
                await self.save_message(user, message)

            # Envoyer le message à tous les membres du chat général
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': f'{user.username}: {message}'  # Envoyer avec l'utilisateur
                }
            )

    async def chat_message(self, event):
        message = event['message']

        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_messages(self):
        # Récupérer uniquement les messages du chat général (recipient=None)
        return list(
            Message.objects.filter(recipient__isnull=True).order_by('-timestamp').values('user__username', 'content')[:50]
        )

    @database_sync_to_async
    def save_message(self, user, content):
        # Sauvegarder le message dans le chat général (recipient=None)
        return Message.objects.create(user=user, content=content, recipient=None)

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']

        # Créer un nom de groupe cohérent basé sur les noms d'utilisateur pour le chat privé
        users = sorted([self.user.username, self.username])
        self.group_name = f'private_chat_{"_".join(users)}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Enregistrer le message dans la base de données uniquement s'il y a un destinataire
        if self.username and self.user.is_authenticated:
            await self.save_message(self.user, self.username, message)

            # Envoyer le message au groupe de chat privé
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user.username}: {message}'
                }
            )
        else:
            await self.close()

    async def chat_message(self, event):
        message = event['message']

        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_message(self, sender, recipient_username, content):
        # Vérifier que le destinataire existe
        try:
            recipient = User.objects.get(username=recipient_username)
            return Message.objects.create(user=sender, recipient=recipient, content=content)
        except User.DoesNotExist:
            return None
