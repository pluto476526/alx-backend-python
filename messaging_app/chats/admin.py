from django.contrib import admin
from .models import User, Conversation, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'participants_list')
    filter_horizontal = ('participants',)
    
    def participants_list(self, obj):
        return ", ".join([user.email for user in obj.participants.all()])

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'sent_at', 'short_body')
    list_filter = ('conversation', 'sender')
    
    def short_body(self, obj):
        return obj.message_body[:50] + '...' if len(obj.message_body) > 50 else obj.message_body
