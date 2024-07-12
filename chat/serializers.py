from rest_framework import serializers
from .models import ChatRoom
from authentication.models import User

class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=User.objects.all(),
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'members']