from rest_framework import serializers
from django.conf import settings
from users.models import User, UserRole, Profile
from roles.models import Role
from groups.models import Group, Assistant, GroupResearcher
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from samples.models import Biosystem, Tissue, Sample, SampleAttachment, SampleTissue, SampleResearcher


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile


class UserListSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=True, required=True)

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date')
