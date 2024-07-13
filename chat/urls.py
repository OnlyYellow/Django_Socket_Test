from django.urls import path
from .views import ChatRoomAPIView, ChatRoomCreateAPIView, AddMemberAPIView

urlpatterns = [
    path('', ChatRoomAPIView.as_view(), name='chat_room_list'),
    path('create_chat', ChatRoomCreateAPIView.as_view(), name='create_chat_room'),
    path('add_member', AddMemberAPIView.as_view(), name='add_member_to_chat_room'),
]