from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

User = get_user_model()

class MessageManager(models.Manager):
    def get_conversation(self, user1, user2):
        """Get all messages between two users in chronological order"""
        return self.filter(
            (Q(sender=user1) & Q(receiver=user2) |
            (Q(sender=user2) & Q(receiver=user1)
        ).select_related('sender', 'receiver', 'parent_message').order_by('timestamp')

    def get_thread(self, root_message):
        """Get a message and all its replies in proper order"""
        return self.filter(
            Q(pk=root_message.pk) | Q(parent_message=root_message)
        ).select_related('sender', 'receiver', 'parent_message').order_by('timestamp')

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(null=True, blank=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    objects = MessageManager()

    def __str__(self):
        sender_name = self.sender.username if self.sender else "[deleted]"
        receiver_name = self.receiver.username if self.receiver else "[deleted]"
        return f"From {sender_name} to {receiver_name} at {self.timestamp}"

    def get_thread_depth(self):
        """Calculate how deep this message is in a thread"""
        depth = 0
        current = self
        while current.parent_message:
            depth += 1
            current = current.parent_message
        return depth

    class Meta:
        ordering = ['timestamp']



class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"History for message {self.message.id} edited at {self.edited_at}"

    class Meta:
        verbose_name_plural = "Message Histories"
        ordering = ['-edited_at']

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"

    class Meta:
        ordering = ['-timestamp']
