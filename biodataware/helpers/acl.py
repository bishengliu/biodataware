from roles.models import Role
from users.models import UserRole
from groups.models import GroupResearcher, Assistant
from django.db.models import Q


def isManger(user):
    try:
        roles = Role.objects.all().filter(role__iexact='Manager')
        ids = [r.id for r in roles]
        userroles = UserRole.objects.all().filter(role_id__in=ids)
        user_role_ids = [u.user_id for u in userroles]
        if user.id in user_role_ids:
            return True
        return False
    except:
        return False


def isInGroups(user, group_ids):
    # get current user group
    try:
        my_Groups = GroupResearcher.objects.all().filter(user_id=user.pk)
        if my_Groups:
            my_group_ids = [g.group_id for g in my_Groups]
            # get the intersection
            inter_groups = list(set(group_ids) & set(my_group_ids))
            if len(inter_groups) > 0:
                return True
        return False
    except:
        return False


def isPIorAssistantofGroup(user, group_ids):
    # check assistants
    assistants = Assistant.objects.all().filter(user_id=user.pk).filter(group_id__in=group_ids)
    if assistants:
        return True
    # check pi
    # check whether user is in one of the groups
    group_researchers = GroupResearcher.objects.all().filter(user_id=user.pk).filter(group_id__in=group_ids)
    if group_researchers:
        # check the role of user to have PI
        userroles = UserRole.objects.all().filter(user_id=user.pk).filter(role__role__iexact="PI")
        if userroles:
            return True
    return False

