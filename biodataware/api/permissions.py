from rest_framework import permissions


# owner otherwise readonly
class IsOwnOrReadOnly(permissions.BasePermission):
    """
        Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `user` attribute.
    """
    def has_object_permission(self, request, view, user):
        if request.method in permissions.SAFE_METHODS:
            return True

        return user == request.user


# only self also have to be the owner
class IsReadOnlyOwner(permissions.BasePermission):
    """
       only self for the permissions.SAFE_METHODS:      
    """
    def has_object_permission(self, request, view, user):
        if request.method in permissions.SAFE_METHODS:
            return user == request.user
        return False


# only the owner can ready and write
# others cannot read at all
class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, user):
        return user == request.user
