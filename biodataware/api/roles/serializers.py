from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from roles.models import Role
from users.models import UserRole


# get, post, delete
# only for PI and Manager
class UserRoleSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = UserRole
        fields = ('role_id', 'role',  'user_id', 'user')


# get all the PIs and Manager
# get, post
class RoleSerializer(serializers.ModelSerializer):
    researchers = UserRoleSerializer(many=True, read_only=True, source='userrole_set')

    class Meta:
        model = Role
        fields = ('pk', 'role', 'description', 'researchers')
