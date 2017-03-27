from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


# Register your models here.
class UserInline(admin.StackedInline):
    model = Profile


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'photo', 'birth', 'is_active', 'is_staff')
    inlines = (UserInline,)

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

admin.site.register(User, UserAdmin)

fields = ('image_tag',)
readonly_fields = ('image_tag',)
