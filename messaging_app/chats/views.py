# chats/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    MessageCreateSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['participants']
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        # Only show conversations the user is part of
        queryset = self.queryset.filter(participants=self.request.user)
        
        # Additional filtering by participant if requested
        participant_id = self.request.query_params.get('participant')
        if participant_id:
            queryset = queryset.filter(participants__id=participant_id)
            
        return queryset.distinct()

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Endpoint to send a message to a specific conversation"""
        conversation = self.get_object()
        serializer = MessageCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save(conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """Create a new conversation with participants"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Automatically add current user to participants
        conversation = serializer.save()
        conversation.participants.add(request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['conversation', 'sender', 'read']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']  # Default ordering
    search_fields = ['message_body']

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        # Only show messages in conversations the user is part of
        queryset = self.queryset.filter(
            conversation__participants=self.request.user
        )
        
        # Additional filtering by conversation if requested
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            queryset = queryset.filter(conversation__id=conversation_id)
            
        return queryset

    def perform_create(self, serializer):
        """Automatically set the sender to the current user"""
        conversation = serializer.validated_data['conversation']
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not part of this conversation")
        serializer.save(sender=self.request.user)
