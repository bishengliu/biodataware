from django.apps import AppConfig


class RolesConfig(AppConfig):
    name = 'roles'

    # auto create user roles
    # only pi is required
    def ready(self):

        from .models import Role
        # add PI role
        pi_role = Role.objects.all().filter(role__exact='PI')
        if not pi_role:
            role_pi = Role.objects.create(role='PI', description='PI')
            role_pi.save()

        # add researcher_role
        researcher_role = Role.objects.all().filter(role__exact='Researcher')
        if not researcher_role:
            role_researcher = Role.objects.create(role='Researcher', description='Researcher')
            role_researcher.save()

        # add manager role
        manager_role = Role.objects.all().filter(role__exact='Manager')
        if not manager_role:
            role_amanager = Role.objects.create(role='Manager', description='Manager')
            role_amanager.save()