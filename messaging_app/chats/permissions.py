from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """
    Allows access only to authenticated users who are participants
    in the target conversation.
    """

    def has_permission(self, request, view):
        # Global-level check: ensure user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level check:
        - obj is expected to be a Conversation or Message instance.
        - User must be a participant in the related Conversation.
        """
        # Handle Conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        # Handle Message objects
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()

        return False

