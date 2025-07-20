# chats/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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

    def get_queryset(self):
        # Only show conversations the user is part of
        return self.queryset.filter(participants=self.request.user)

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

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        # Only show messages in conversations the user is part of
        return self.queryset.filter(
            conversation__participants=self.request.user
        )

    def perform_create(self, serializer):
        """Automatically set the sender to the current user"""
        conversation = serializer.validated_data['conversation']
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not part of this conversation")
        serializer.save(sender=self.request.user)from django.shortcuts import render

# Create your views here.
