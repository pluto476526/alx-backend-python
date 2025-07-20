from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    # Adding CharField for demonstration
    display_name = serializers.CharField(
        source='get_full_name',
        read_only=True,
        help_text="Combination of first and last name"
    )
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'display_name', 'phone_number', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        """Ensure email is unique (handled by model, but explicit in serializer)"""
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value.lower()

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField(
        max_length=2000,
        min_length=1,
        trim_whitespace=False,
        help_text="Message content (1-2000 characters)"
    )
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'message_body', 'sent_at', 'read']
        read_only_fields = ['id', 'sender', 'sent_at', 'read']

    def validate_message_body(self, value):
        """Custom message validation"""
        if len(value.strip()) == 0:
            raise ValidationError("Message cannot be empty")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True,
        help_text="List of participant user IDs"
    )
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participant_ids', 'messages', 'created_at']
        read_only_fields = ['id', 'participants', 'created_at', 'messages']

    def validate_participant_ids(self, value):
        """Validate participant IDs"""
        if len(value) < 2:
            raise ValidationError("Conversation must have at least 2 participants")
        
        # Check if users exist
        existing_users = User.objects.filter(id__in=value).count()
        if existing_users != len(value):
            raise ValidationError("One or more participants do not exist")
            
        return value

    def create(self, validated_data):
        """Create conversation with participants"""
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create()
        
        # Add participants including the current user
        current_user = self.context['request'].user
        all_participants = set(participant_ids) | {current_user.id}
        
        for user_id in all_participants:
            user = User.objects.get(id=user_id)
            conversation.participants.add(user)
        
        return conversation

    def to_representation(self, instance):
        """Custom representation to include only recent messages"""
        representation = super().to_representation(instance)
        
        # Limit messages to last 20 for performance
        representation['messages'] = MessageSerializer(
            instance.messages.order_by('-sent_at')[:20],
            many=True,
            context=self.context
        ).data
        
        return representation


class MessageCreateSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField(
        max_length=2000,
        min_length=1,
        required=True,
        help_text="Message content (1-2000 characters)"
    )
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'message_body']
        read_only_fields = ['id']

    def validate(self, data):
        """Validate that user is part of the conversation"""
        user = self.context['request'].user
        conversation = data.get('conversation')
        
        if not conversation.participants.filter(id=user.id).exists():
            raise ValidationError("You are not part of this conversation")
            
        return data

    def create(self, validated_data):
        """Create message with sender and conversation validation"""
        message = Message.objects.create(
            sender=self.context['request'].user,
            **validated_data
        )
        return message
