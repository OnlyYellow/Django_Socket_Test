import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from mysite import settings
from urllib.parse import parse_qs
from .models import ChatRoom
from rest_framework_simplejwt.tokens import AccessToken
from authentication.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL에서 room_name 추출
        query_string = parse_qs(self.scope['query_string'].decode())
        self.room_name = query_string.get('room_name', [None])[0]
        self.room_group_name = f'chat_{self.room_name}'

        # 쿠키에서 JWT 토큰을 읽어옴
        cookie_header = next((value for name, value in self.scope['headers'] if name == b'cookie'), None)
        if cookie_header:
            # 쿠키 문자열 디코드
            cookies = cookie_header.decode()
            # 'access' 토큰 추출
            token = self.extract_jwt_from_cookie(cookies, 'access')

            if token:
                self.user = await self.get_user_from_token(token)
                if self.user:
                    # 토큰으로부터 사용자 인증
                    user = self.user
                    # 채팅방 멤버 확인
                    if await self.is_room_member(user, self.room_name):
                        await self.channel_layer.group_add(
                            self.room_group_name,
                            self.channel_name
                        )
                    await self.accept()
                    return
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
        user_email = self.user.email

        # Send message to room group
        if self.user:
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

    def extract_jwt_from_cookie(self, cookie_str, key):
        # 쿠키 문자열에서 특정 키('access')의 JWT 값을 추출
        try:
            # 쿠키 키-값 쌍을 파싱
            cookies = dict(x.strip().split('=') for x in cookie_str.split(';'))
            return cookies.get(key)
        except ValueError:
            # 쿠키 문자열 파싱 중 오류 발생 시
            return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # 토큰 디코드 (여기서는 'SECRET_KEY'를 사용)
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data['user_id']
            user = User.objects.get(id=user_id)
            return user
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
        except User.DoesNotExist:
            print("User does not exist")
            return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
        
    @database_sync_to_async
    def is_room_member(self, user, room_name):
        room = ChatRoom.objects.get(name=room_name)
        return user in room.members.all()