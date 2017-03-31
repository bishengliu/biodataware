from rest_framework import serializers
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
import re
from helpers.validators import validate_phone
from users.models import User, UserRole, Profile
from roles.models import Role
from groups.models import Group, Assistant, GroupResearcher
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from samples.models import Biosystem, Tissue, Sample, SampleAttachment, SampleTissue, SampleResearcher


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('photo', 'photo_tag', 'birth_date', 'telephone')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', 'email', 'profile')


class UserDetailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    first_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    last_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    birth_date = serializers.DateField(required=False, allow_null=True, input_formats=settings.DATE_INPUT_FORMATS)
    photo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True, max_length=100)
    telephone = serializers.CharField(validators=[validate_phone], allow_null=True, allow_blank=True, max_length=20)

    def validate(self, data):
        user = get_object_or_404(User, pk=self.initial_data['pk'])
        users = User.objects.exclude(username__iexact=user.username).filter(email__iexact=data['email'])
        if users.count() <= 1:
            return data
        raise serializers.ValidationError(_("The email already taken"))


class PasswordSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    old_password = serializers.CharField(required=True, allow_blank=False)
    new_password = serializers.CharField(required=True, allow_blank=False)

    def validate_new_password(self, value):
        password_pattern = re.compile("^(?=.*[A-Z])(?=.*[a-z].*[a-z])(?=.*[0-9].*[0-9]).{8,}$")
        msg = _("Password contains at least: " \
              "1 uppercase letter, 2 lowercase letters, 2 digits and must be longer than 8 characters.")
        if not password_pattern.search(value):
            raise serializers.ValidationError(msg)

    def validate(self, data):
        try:
            if not authenticate(username=data['username'], password=data['old_password']):
                raise serializers.ValidationError(_("Username or password incorrect!"))
            return data
        except:
            raise serializers.ValidationError(_("Username or password incorrect!"))




