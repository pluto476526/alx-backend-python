from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        """Return unread messages for a specific user"""
        return self.filter(
            receiver=user,
            is_read=False
        ).select_related('sender').only(
            'id', 'content', 'timestamp', 'sender__username'
        )

