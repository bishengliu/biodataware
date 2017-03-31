from rest_framework import permissions


class IsOwnOrReadOnly(permissions.BasePermission):
    """
        Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `user` attribute.
    """
    def has_object_permission(self, request, view, user):
        if request.method in permissions.SAFE_METHODS:
            return True

        return user == request.user
