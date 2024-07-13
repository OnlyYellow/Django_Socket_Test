import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from .models import ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            # 쿼리 스트링에서 room_name 추출
            query_string = parse_qs(self.scope['query_string'].decode('utf-8'))
            room_name = query_string.get('room_name', [None])[0]

            if room_name is None:
                print("no room name")
                await self.close()
                return
            
            # 멤버십 검증
            room = await self.get_room(room_name)
            if room and await self.is_room_member(room, user):
                self.room_group_name = f'chat_{room_name}'

                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_email = self.scope["user"].email

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'email': user_email,
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        email = event['email']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'email': email,
            'message': message
        }))

    @database_sync_to_async
    def get_room(self, room_name):
        try:
            return ChatRoom.objects.get(name=room_name)
        except ChatRoom.DoesNotExist:
            return None
        
    @database_sync_to_async
    def is_room_member(self, room, user):
        return user in room.members.all()