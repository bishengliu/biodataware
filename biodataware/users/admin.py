from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, UserRole
from django.contrib.auth.models import Group


# user profile
class UserInline(admin.StackedInline):
    model = Profile


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'photo', 'email', 'first_name', 'last_name', 'birth', 'is_active')
    inlines = [UserInline, ]

    def photo(self, obj):
        try:
            return obj.profile.photo_tag()
        except:
            return None

    photo.short_description = 'Photo'
    photo.allow_tags = True

    def birth(self, obj):
        try:
            return obj.profile.birth_date
        except:
            return None

    birth.short_description = 'Birth Date'

# register user and profile
admin.site.register(User, UserAdmin)

fields = ('image_tag',)
readonly_fields = ('image_tag',)


# user roles
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'role', 'description']

    def email(self, obj):
        try:
            return obj.user.email
        except:
            return None

    email.short_description = 'Email'

    def description(self, obj):
        try:
            return obj.role.description
        except:
            return None

    description.short_description = 'Description'


# register user role
admin.site.register(UserRole, UserRoleAdmin)


# un-register groups from admin dashboard
admin.site.unregister(Group)
