from rest_framework import permissions
from users.models import UserRole
from roles.models import Role
from groups.models import Group, GroupResearcher, Assistant
from containers.models import GroupContainer
from django.conf import settings


# only the owner have the read access
class IsReadOnlyOwner(permissions.BasePermission):
    """
       only self for the permissions.SAFE_METHODS:      
    """
    def has_object_permission(self, request, view, obj):
        try:
            if request.method in permissions.SAFE_METHODS:
                return obj['user'] == request.user
            return False
        except:
            return False


# only the owner can ready and write
class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            return obj['user'] == request.user
        except:
            return False


# owner write access, others readonly
class IsOwnOrReadOnly(permissions.BasePermission):
    """
        Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        try:
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj['user'] == request.user
        except:
            return False


# check whether in the same group
# read only
class IsInGroupReadonly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            auth_user = request.user
            if auth_user.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            user_group_ids = [g.id for g in user_groups]

            if request.user.is_authenticated():
                groups = GroupResearcher.objects.all().filter(group__email=auth_user.email)
                if not groups:
                    return False
                group_ids = [g.id for g in groups]
                # get the intersection
                inter_ids = list(set(user_group_ids) & set(group_ids))
                if len(inter_ids) >= 1:
                    # in the same group
                    # safe request
                    if request.method in permissions.SAFE_METHODS:
                        return True
            return False
        except:
            return False


# write and read access
class IsInGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            auth_user = request.user
            if auth_user.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            user_group_ids = [g.id for g in user_groups]

            if request.user.is_authenticated():
                groups = GroupResearcher.objects.all().filter(group__email=auth_user.email)
                if not groups:
                    return False
                group_ids = [g.id for g in groups]
                # get the intersection
                inter_ids = list(set(user_group_ids) & set(group_ids))
                if len(inter_ids) >= 1:
                    # in the same group
                        return True
            return False
        except:
            return False


# PI must be related to the groups
# current user is the pi
# does not check whether the target user is in the group

# pi must have a group
# PI read only
class IsPIReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            authUser = request.user
            if authUser.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            if request.user.is_authenticated():
                # find the roles
                role = Role.objects.all().filter(role__iexact='PI').first()
                if not role:
                    return False
                pi_role = UserRole.objects.all().filter(user_id=authUser.id).filter(role_id=role.id).first()
                if pi_role:
                    if request.method in permissions.SAFE_METHODS:
                        return True
            return False
        except:
            return False


# pi must have a group
# PI write and read access
class IsPI(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            authUser = request.user
            if authUser.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            if request.user.is_authenticated():
                # find the roles
                role = Role.objects.all().filter(role__iexact='PI').first()
                if not role:
                    return False
                pi_role = UserRole.objects.all().filter(user_id=authUser.id).filter(role_id=role.id).first()
                if pi_role:
                    return True
            return False
        except:
            return False


class IsPIorReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            if request.method in permissions.SAFE_METHODS:
                return True

            authUser = request.user
            if authUser.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            if request.user.is_authenticated():
                # find the roles
                role = Role.objects.all().filter(role__iexact='PI').first()
                if not role:
                    return False
                pi_role = UserRole.objects.all().filter(user_id=authUser.id).filter(role_id=role.id).first()
                if pi_role:
                    return True
            return False
        except:
            return False


# pi must have a group
# current user is the pi of the user
# must be in the same group
# read, write access
class IsPIofUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            authUser = request.user
            if authUser.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            user_group_ids = [g.id for g in user_groups]
            # check authUser
            if request.user.is_authenticated():
                # check whether current user is one of the PI
                role = Role.objects.all().filter(role__iexact='PI').first()
                if not role:
                    return False
                pi_roles = UserRole.objects.all().filter(user_id=authUser.id).filter(role_id=role.id)
                if not pi_roles:
                    return False
                # check whether there is a group created for PI
                pi_groups = Group.objects.all().filter(email__iexact=authUser.email)
                if pi_groups:
                    pi_group_ids = [g.id for g in pi_groups]
                    intersection = list(set(user_group_ids) & set(pi_group_ids))
                    if len(intersection) >= 1:
                        return True
            return False
        except:
            return False


# readonly
class IsPIofUserReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            authUser = request.user
            if authUser.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            user_group_ids = [g.id for g in user_groups]
            # check authUser
            if request.user.is_authenticated():
                # check whether current user is one of the PI
                role = Role.objects.all().filter(role__iexact='PI').first()
                if not role:
                    return False
                pi_roles = UserRole.objects.all().filter(user_id=authUser.id).filter(role_id=role.id)
                if not pi_roles:
                    return False
                # check whether there is a group created for PI
                pi_groups = Group.objects.all().filter(email__iexact=authUser.email)
                if pi_groups:
                    pi_group_ids = [g.id for g in pi_groups]
                    intersection = list(set(user_group_ids) & set(pi_group_ids))
                    if len(intersection) >= 1:
                        if request.method in permissions.SAFE_METHODS:
                            return True
            return False
        except:
            return False


# user must be in the same group
# write and read access
class IsPIorAssistantofUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # user must be in the same group
        try:
            auth_user = request.user
            if auth_user.is_superuser:
                return True
            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            user_group_ids = [g.id for g in user_groups]

            if request.user.is_authenticated():
                # pi
                role = Role.objects.all().filter(role__iexact='PI').first()
                if role:
                    # pi
                    pi_roles = UserRole.objects.all().filter(user_id=auth_user.id).filter(role_id=role.id)
                    if pi_roles:
                        # pi
                        pi_groups = Group.objects.all().filter(email__iexact=auth_user.email)
                        if pi_groups:
                            pi_group_ids = [g.id for g in pi_groups]
                            intersection = list(set(user_group_ids) & set(pi_group_ids))
                            if len(intersection) >= 1:
                                    return True
                    else:
                        # assistants
                        # get the group
                        auth_groups = GroupResearcher.objects.all().filter(user_id=auth_user.id)
                        if auth_groups:
                            auth_group_ids = [g.id for g in auth_groups]
                            assistant_groups = Assistant.objects.all().filter(group_id__in=auth_group_ids)
                            if assistant_groups:
                                assistant_group_ids = [a.group_id for a in assistant_groups]
                                intersection = list(set(user_group_ids) & set(assistant_group_ids))
                                if len(intersection) >= 1:
                                    return True
            return False
        except:
            return False


# read only
class IsPIorAssistantofUserReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # user must be in the same group
        try:
            auth_user = request.user
            if auth_user.is_superuser:
                return True

            user = obj['user']
            # first check whether the user is in any group
            user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
            if not user_groups:
                return False
            user_group_ids = [g.id for g in user_groups]

            if request.user.is_authenticated():
                # pi
                role = Role.objects.all().filter(role__iexact='PI').first()
                if role:
                    # pi
                    pi_roles = UserRole.objects.all().filter(user_id=auth_user.id).filter(role_id=role.id)
                    if pi_roles:
                        # pi
                        pi_groups = Group.objects.all().filter(email__iexact=auth_user.email)
                        if pi_groups:
                            pi_group_ids = [g.id for g in pi_groups]
                            intersection = list(set(user_group_ids) & set(pi_group_ids))
                            if len(intersection) >= 1:
                                if request.method in permissions.SAFE_METHODS:
                                    return True
                    else:
                        # assistants
                        # get the group
                        auth_groups = GroupResearcher.objects.all().filter(user_id=auth_user.id)
                        if auth_groups:
                            auth_group_ids = [g.id for g in auth_groups]
                            assistant_groups = Assistant.objects.all().filter(group_id__in=auth_group_ids)
                            if assistant_groups:
                                assistant_group_ids = [a.group_id for a in assistant_groups]
                                intersection = list(set(user_group_ids) & set(assistant_group_ids))
                                if len(intersection) >= 1:
                                    if request.method in permissions.SAFE_METHODS:
                                        return True
            return False
        except:
            return False


class IsPIorAssistantofUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            auth_user = request.user
            if auth_user.is_authenticated():
                if auth_user.is_superuser:
                    return True

                user = obj['user']
                # first check whether the user is in any group
                user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
                if not user_groups:
                    return False
                user_group_ids = [g.id for g in user_groups]

                # pi role
                role = Role.objects.all().filter(role__iexact='PI').first()
                if role:
                    pi_roles = UserRole.objects.all().filter(user_id=auth_user.id).filter(role_id=role.id)
                    if pi_roles:
                        pi_groups = Group.objects.all().filter(email__iexact=auth_user.email)
                        if pi_groups:
                            pi_group_ids = [g.id for g in pi_groups]
                            intersection = list(set(user_group_ids) & set(pi_group_ids))
                            if len(intersection) >= 1:
                                return True
                    else:
                        auth_groups = GroupResearcher.objects.all().filter(user_id=auth_user.id)
                        if auth_groups:
                            auth_group_ids = [g.id for g in auth_groups]
                            assistant_groups = Assistant.objects.all().filter(group_id__in=auth_group_ids)
                            if assistant_groups:
                                assistant_group_ids = [a.group_id for a in assistant_groups]
                                intersection = list(set(user_group_ids) & set(assistant_group_ids))
                                if len(intersection) >= 1:
                                    return True
                            else:
                                # normal researchers in the group
                                intersection = list(set(user_group_ids) & set(auth_group_ids))
                                if len(intersection) >= 1:
                                    if request.method in permissions.SAFE_METHODS:
                                        return True
            return False
        except:
            return False


# must pass container object to the obj
class IsInGroupContanier(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            user = request.user
            if user.is_superuser:
                return True
            container = obj['container']
            #get the group containers
            group_containers = GroupContainer.objects.all().filter(container_id=container.pk)
            if group_containers:
                # get the group ids
                container_group_ids = [g.group_id for g in group_containers]
                if len(container_group_ids) > 0:
                    # get the current user group
                    group_researchers = GroupResearcher.objects.all().filter(user_id=user.pk).filter(group_id__in=container_group_ids)
                    if group_researchers:
                        return True
            return False
        except:
            return False


# obj must contain container
class IsInGroupBox(permissions.BasePermission):
    pass
