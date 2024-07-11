from django.urls import path
from .views import ChatRoomCreateAPIView

urlpatterns = [
    path('create_chat/', ChatRoomCreateAPIView.as_view(), name='create_chat_room'),
]