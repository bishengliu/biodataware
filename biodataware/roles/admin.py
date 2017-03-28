from django.contrib import admin
from .models import Role


# Register your models here.
class RoleAdmin(admin.ModelAdmin):
    list_display('role', 'description')

admin.site.register(Role)

