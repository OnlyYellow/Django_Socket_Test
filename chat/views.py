from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatRoomSerializer, AddMemberSerializer
from .models import ChatRoom
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication


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

    def post(self, request, room_id):
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response({"message": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddMemberSerializer(data=request.data, instance=chat_room)
        if serializer.is_valid():
            serializer.save()
            return Response(ChatRoomSerializer(chat_room).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)