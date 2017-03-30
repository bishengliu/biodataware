from rest_framework import serializers
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
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

'''
# http://www.django-rest-framework.org/tutorial/1-serialization/
class UserDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.RegexField(regex=r'^\w+$', required=True, allow_blank=False, max_length=30)
    email = serializers.EmailField(required=True, allow_blank=False)
    first_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    last_name = serializers.RegexField(regex=r'^\w+$', required=False, allow_blank=True, max_length=30)
    birth_date = serializers.DateField(required=False, allow_null=True, input_formats=settings.DATE_INPUT_FORMATS)
    photo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True, max_length=100)
    telephone = serializers.CharField(validators=[validate_phone], null=True, blank=True, max_length=20)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

'''
