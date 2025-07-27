from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email already exists")
        return value

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField(
        max_length=2000,
        min_length=1,
        help_text="Message content (1-2000 characters)"
    )

    class Meta:
        model = Message
        fields = ['id', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['id', 'sender', 'sent_at']

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participant_ids', 'messages', 'created_at']
        read_only_fields = ['id', 'participants', 'created_at']

    def get_messages(self, obj):
        messages = obj.messages.order_by('-sent_at')[:20]
        return MessageSerializer(messages, many=True, context=self.context).data

    def validate_participant_ids(self, value):
        if len(value) < 1:
            raise ValidationError("At least one participant required")
        if len(value) != len(set(value)):
            raise ValidationError("Duplicate participants not allowed")
        return value

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create()
        
        current_user = self.context['request'].user
        all_participants = set(participant_ids) | {current_user.id}
        
        for user_id in all_participants:
            try:
                user = User.objects.get(id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                raise ValidationError(f"User with ID {user_id} does not exist")
        
        return conversation
