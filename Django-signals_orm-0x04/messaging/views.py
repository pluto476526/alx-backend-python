from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Message


User = get_user_model()

@login_required
def conversation_view(request, user_id):
    receiver = get_object_or_404(User, pk=user_id)
    sender=request.user
    messages = Message.objects.filter(
        Q(sender=sender, receiver=receiver) |
        Q(sender=receiver, receiver=sender)
    ).select_related('sender', 'receiver', 'parent_message').order_by('timestamp')
    
    return render(request, 'messaging/conversation.html', {
        'receiver': receiver,
        'messages': messages
    })


@login_required
def thread_view(request, message_id):
    root_message = get_object_or_404(Message, pk=message_id)
    thread = Message.objects.get_thread(root_message)
    return render(request, 'messaging/thread.html', {
        'root_message': root_message,
        'thread': thread
    })


@login_required
def unread_messages(request):
    unread_messages = Message.unread.unread_for_user(request.user).only(
        'id', 'content', 'timestamp', 'sender__username'
    )

    return render(request, 'messaging/unread_messages.html', {
        'unread_messages': unread_messages
    })


def delete_user(request):
    user = request.user
    user.delete()
    messages.success(request, "Your account has been deleted.")
    return redirect('home')  # Replace 'home' with your actual home URL name
