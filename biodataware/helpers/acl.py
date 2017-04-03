from roles.models import Role
from users.models import UserRole
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
