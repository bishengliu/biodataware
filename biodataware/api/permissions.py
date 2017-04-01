from rest_framework import permissions
from users.models import UserRole
from roles.models import Role
from groups.models import Group, GroupResearcher, Assistant

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


# current user is the pi
# does not check whether the target user is in the group
class IsPI(permissions.BasePermission):

    def has_object_permission(self, request, view, user):
        if request.user.is_authenticated():
            authUser = request.user
            # find the roles
            role = Role.objects.all().filter(role__iexact='PI').first()
            if role is None:
                return False
            pi_role = UserRole.objects.all().filter(user_id=authUser.id).filter(role_id=role.id).first()
            if pi_role is not None:
                return True

        return False


# current user is the pi of the user
class IsPIofUser(permissions.BasePermission):

    def has_object_permission(self, request, view, user):
        # first check whether the user is in any group
        user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
        if not user_groups:
            return  False
        user_group_ids = [g.id for g in user_groups]
        # check authUser
        if request.user.is_authenticated():
            authUser = request.user
            # check whether current user is one of the PI
            role = Role.objects.all().filter(role__iexact='PI').first()
            if role is None:
                return False
            pi_role = UserRole.objects.all().filter(user_id=authUser.id).filter(role_id=role.id).first()
            if pi_role is None:
                return False
            # check whether there is a group created for PI
            # case one authUser == group emial
            groups1 = Group.objects.all().filter(email__iexact=authUser.email)
            if groups1.count() >= 1:
                group1_ids = [g.id for g in groups1]
                intersection1 = user_group_ids & group1_ids
                if intersection1.count() >= 1:
                    return True
            else:
                # case tow authUser != group email
                # find the group from groupresearcher, which means authUser is added to a group(s)
                groups2 = GroupResearcher.objects.all().filter(group__email=authUser.emai)
                if not groups2:
                    return False
                group2_ids = [g.id for g in groups2]
                intersection2 = user_group_ids & group2_ids
                if intersection2.count() >= 1:
                    return True

        return False


# current user is the assistants of a PI the supervising the target user
class IsPIAssistantofUser(permissions.BasePermission):

    def has_object_permission(self, request, view, user):
        # first check whether the user is in any group
        user_groups = GroupResearcher.objects.all().filter(user_id=user.id)
        if not user_groups:
            return False
        user_group_ids = [g.id for g in user_groups]

        if request.user.is_authenticated():
            # check the user groups
            assisUser = request.user
            groups = GroupResearcher.objects.all().filter(group__email=assisUser.emai)
            if not groups:
                return False
            group_ids = [g.id for g in groups]
            #get the intersection
            inter_ids = user_group_ids & group_ids
            if inter_ids.count() >= 1:
                assistants = Assistant.objects.all().filter(group_id__in=inter_ids)
                if not assistants:
                    return False
                else:
                    return True

        return False
