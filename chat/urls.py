from django.urls import path
from .views import ChatRoomCreateAPIView, AddMemberAPIView

urlpatterns = [
    path('create_chat/', ChatRoomCreateAPIView.as_view(), name='create_chat_room'),
    path('add_member/<int:room_id>/', AddMemberAPIView.as_view(), name='add_member_to_chat_room'),
]