# chats/urls.py
from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'api/conversations', ConversationViewSet, basename='conversation')
router.register(r'api/messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
