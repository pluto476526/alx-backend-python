from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """Allow access only if user is a participant in the conversation"""

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()

