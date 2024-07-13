from rest_framework import serializers
from .models import ChatRoom
from authentication.models import User

class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field='email',
        queryset=User.objects.all(),
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'members']


class AddMemberSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return value

    def update(self, instance, validated_data):
        user = User.objects.get(email=validated_data['email'])
        instance.members.add(user)
        instance.save()
        return instance