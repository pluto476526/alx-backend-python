from rest_framework.permissions import BasePermission

class IsParticipant(BasePermission):
    """Allow access only if user is a participant in the conversation"""

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()

