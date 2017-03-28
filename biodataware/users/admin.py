from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, UserRole
from django.contrib.auth.models import Group


# Register your models here.
class UserInline(admin.StackedInline):
    model = Profile


class UserRoleInline(admin.StackedInline):
    model = UserRole


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'photo', 'birth', 'is_active', 'role')
    inlines = (UserInline, UserRoleInline)

    def photo(self, obj):
        try:
            return obj.profile.photo_tag()
        except:
            return None

    photo.short_description = 'User Photo'
    photo.allow_tags = True

    def birth(self, obj):
        try:
            return obj.profile.birth_date
        except:
            return None

    birth.short_description = 'Birth Date'

    def role(self, obj):
        try:
            return obj.userRole.role
        except:
            return None

admin.site.register(User, UserAdmin)

fields = ('image_tag',)
readonly_fields = ('image_tag',)


# unregister groups from admin dashboard
admin.site.unregister(Group)
