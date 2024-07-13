from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatRoomSerializer, AddMemberSerializer
from .models import ChatRoom
from authentication.models import User
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication


class ChatRoomAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        email = request.user.email
        user = User.objects.get(email=email)

        # 현재 사용자가 멤버인 채팅방만 필터링
        chat_rooms = ChatRoom.objects.filter(members = user)

        # 채팅방 정보와 각 채팅방의 멤버들의 email을 반환
        data = [
            {
                "room_id": room.id,
                "name": room.name,
                "members": [member.email for member in room.members.all()]
            }
            for room in chat_rooms
        ]

        return Response(data, status=status.HTTP_200_OK)


class ChatRoomCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():

            # 채팅방 생성
            chat_room = serializer.save()
            chat_room.members.add(request.user)  # 방 생성자를 자동으로 멤버에 추가
            chat_room.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AddMemberAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        room_name = request.query_params.get('room_name')
        if not room_name:
            return Response({
                "message": "The Room name parameter is missing"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

        chat_room = get_object_or_404(ChatRoom, name=room_name)

        serializer = AddMemberSerializer(data=request.data, instance=chat_room)
        if serializer.is_valid():
            serializer.save()
            return Response(ChatRoomSerializer(chat_room).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)