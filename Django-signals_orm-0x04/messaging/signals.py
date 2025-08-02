from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory
from django.utils import timezone

User = get_user_model()

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created and instance.receiver:  # Check if receiver exists
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content changed
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                instance.edited = True
                instance.last_edited = timezone.now()
        except Message.DoesNotExist:
            pass  # New message, nothing to compare

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    # Clean up messages where user was sender or receiver
    Message.objects.filter(sender=instance).update(sender=None)
    Message.objects.filter(receiver=instance).update(receiver=None)
    
    # Delete notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Clean up message history where user was editor
    MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)
