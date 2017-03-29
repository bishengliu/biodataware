from django.contrib import admin
from .models import Group, Assistant, GroupResearcher


# Register researcher group.
class GroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'photo_tag', 'pi', 'pi_fullname', 'email', 'telephone', 'department']

admin.site.register(Group, GroupAdmin)


# register assistant
class AssistantAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'pi', 'username', 'email']

    def group_name(self, obj):
        try:
            return obj.group.group_name
        except:
            return None

    group_name.short_description = 'Group Name'

    def pi(self, obj):
        try:
            return obj.group.pi
        except:
            return None

    pi.short_description = 'PI'

    def username(self, obj):
        try:
            return obj.user.username
        except:
            return None

    username.short_description = 'Researcher'

    def email(self, obj):
        try:
            return obj.user.email
        except:
            return None

        email.short_description = 'Email'


# register user role
admin.site.register(Assistant, AssistantAdmin)


# register researchers
class ResearcherAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'pi', 'username', 'email']

    def group_name(self, obj):
        try:
            return obj.group.group_name
        except:
            return None

    group_name.short_description = 'Group Name'

    def pi(self, obj):
        try:
            return obj.group.pi
        except:
            return None

    pi.short_description = 'PI'

    def username(self, obj):
        try:
            return obj.user.username
        except:
            return None

    username.short_description = 'Researcher'

    def email(self, obj):
        try:
            return obj.user.email
        except:
            return None

        email.short_description = 'Email'


# register user role
admin.site.register(GroupResearcher, ResearcherAdmin)
