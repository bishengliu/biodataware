from rest_framework import serializers
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
import re
from helpers.validators import validate_phone
from users.models import User, UserRole, Profile
from roles.models import Role
from groups.models import GroupResearcher


# get the groups that the researcher belongs to
class GroupResearcherSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField()

    class Meta:
        model = GroupResearcher
        fields = ('group_id', 'group')


# user role
class UserRoleSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = UserRole
        fields = ('pk', 'role_id', 'role',  'user_id', 'user')


class UserRoleCreateSerializer(serializers.Serializer):

    role_id = serializers.IntegerField(required=True, allow_null=False)
    user_id = serializers.IntegerField(required=True, allow_null=False)

    def validate_role_id(self, value):
        try:
            Role.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError(_("Invalid Role!"))

    def validate_user_id(self, value):
        try:
            User.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError(_("User doesn't exist!"))

    def validate(self, data):
        try:
            UserRole.objects.all().filter(user_id=data['user_id']).filter(role_id=data['role_id'])
            return data
        except:
            raise serializers.ValidationError(_("Role already exist for the target user!"))


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('photo', 'photo_tag', 'birth_date', 'telephone')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    roles = serializers.StringRelatedField(many=True, source='userrole_set') # reverse with set
    #userrole_set = UserRoleSerializer(many=True, read_only=True)
    #groups = serializers.StringRelatedField(many=True, source='groupresearcher_set') # reverse with set
    #groups = GroupResearcherSerializer(many=True, read_only=True, source='groupresearcher_set')

    class Meta:
        model = User
        fields = ('pk', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'profile', 'roles')
        #fields = ('pk', 'username', 'first_name', 'last_name', 'email', 'profile', 'roles', 'userrole_set', 'groups', 'groupresearcher_set')


class UserDetailUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    first_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    last_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    birth_date = serializers.DateField(required=False, allow_null=True, input_formats=settings.DATE_INPUT_FORMATS)
    photo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True, max_length=100)
    telephone = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=20)


class PasswordSerializer(serializers.Serializer):
    # username = serializers.CharField(read_only=True)
    old_password = serializers.CharField(required=True, allow_blank=False)
    new_password = serializers.CharField(required=True, allow_blank=False)

    def validate_new_password(self, value):
        password_pattern = re.compile("^(?=.*[A-Z])(?=.*[a-z].*[a-z])(?=.*[0-9].*[0-9]).{8,}$")
        msg = _("Password contains at least: " \
              "1 uppercase letter, 2 lowercase letters, 2 digits and must be longer than 8 characters.")
        if not password_pattern.search(value):
            raise serializers.ValidationError(msg)
        return value


class UserCreateSerializer(serializers.Serializer):
    username = serializers.RegexField(regex=r'^\w+$', required=True)
    email = serializers.EmailField(required=True, allow_blank=False)
    password1 = serializers.CharField(required=True, max_length=30)
    password2 = serializers.CharField(required=True, max_length=30)
    first_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    last_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    birth_date = serializers.DateField(required=False, allow_null=True, input_formats=settings.DATE_INPUT_FORMATS)
    photo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True, max_length=100)
    telephone = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=20)

    def validated_username(self, value):
        try:
            User.objects.get(username__iexact=value)
        except User.DoesNotExist:
            return value
        raise serializers.ValidationError(_("username already taken!"))

    def validated_email(self, value):
        try:
            User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            return value
        raise serializers.ValidationError(_("email already taken!"))

    def validate(self, data):
        if 'password1' in data and 'password2' in data:
            if data.get('password1') != data.get('password2'):
                raise serializers.ValidationError(_("passwords do not match!"))
            password_pattern = re.compile("^(?=.*[A-Z])(?=.*[a-z].*[a-z])(?=.*[0-9].*[0-9]).{8,}$")
            if not password_pattern.search(data.get('password1')):
                msg = "Password contains at least: " \
                      "1 uppercase letter, 2 lowercase letters, 2 digits and must be longer than 8 characters."
                raise serializers.ValidationError(_(msg))
            return data

        msg = _("Something went wrong, validation failed")
        raise serializers.ValidationError(msg)


# class for get token
class LoginSerializer(serializers.Serializer):
    username = serializers.RegexField(regex=r'^\w+$', required=True)
    password = serializers.CharField(required=True, max_length=30)
