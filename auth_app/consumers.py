
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Connect to the WebSocket
        self.sender = self.scope['user']
        self.receiver_username = self.scope['url_route']['kwargs']['receiver_username']

        # Check if the sender and receiver are active users
        if not User.objects.filter(username=self.receiver_username, is_active=True).exists():
            await self.close()
            return

        self.room_name = self.get_room_name(self.sender.username, self.receiver_username)
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Disconnect from the WebSocket
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive a message from the WebSocket
        data = json.loads(text_data)
        message_content = data['message']

        # Create and save the message in the database
        message = Message(
            sender=self.sender,
            receiver=User.objects.get(username=self.receiver_username),
            content=message_content,
            timestamp=timezone.now()  # Set the current timestamp
        )
        message.save()


        # Broadcast the message to the specific room (sender and receiver)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message_content
            }
        )

    async def chat_message(self, event):
        # Send a message to the WebSocket
        message = event['message']

        # Send the message to the connected user
        await self.send(text_data=json.dumps({
            'message': message
        }))

    def get_room_name(self, sender_username, receiver_username):
        #creating a unique name for the room
        return f"{sender_username}_{receiver_username}"


