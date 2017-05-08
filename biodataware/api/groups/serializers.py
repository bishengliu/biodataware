from rest_framework import serializers
from groups.models import Group, GroupResearcher, Assistant
from users.models import UserRole, User
from django.utils.translation import ugettext_lazy as _
from users.models import Profile
from django.shortcuts import get_object_or_404
from django.conf import settings
from api.users.serializers import UserSerializer


# no view
class AssistantSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = GroupResearcher
        fields = ('user_id', 'user')


# no view
class GroupResearcherSerializer(serializers.ModelSerializer):
    #user = serializers.StringRelatedField()
    user = UserSerializer()

    class Meta:
        model = GroupResearcher
        fields = ('user_id', 'user')


# get, post, delete
class GroupSerializer(serializers.ModelSerializer):
    researchers = GroupResearcherSerializer(many=True, read_only=True, source='groupresearcher_set')
    assistants = AssistantSerializer(many=True, read_only=True, source='assistant_set')

    class Meta:
        model = Group
        fields = ('pk', 'group_name', 'pi', 'pi_fullname', 'photo', 'photo_tag', 'email', 'telephone', 'department', 'assistants',
                  'researchers')


# group detail
class GroupDetailCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('group_name', 'pi', 'pi_fullname', 'photo', 'email', 'telephone', 'department')


# for assign researcher to a group
class GroupResearcherCreateSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(read_only=False)
    group_id = serializers.IntegerField(read_only=False)

    class Meta:
        model = GroupResearcher
        fields = ('user_id', 'group_id')

    def validate_user_id(self, value):
        get_object_or_404(User, pk=value)
        return value

    def validate_group_id(self, value):
        get_object_or_404(Group, pk=value)
        return value
    """
        def validate(self, data):
        if 'user_id' in data and 'group_id' in data:
            group_researcher = GroupResearcher.objects.all()\
                .filter(user_id=data['user_id'])\
                .filter(group_id=data['group_id'])
            if group_researcher:
                msg = _("Researcher already in the group!")
                raise serializers.ValidationError(msg)
            return data
        msg = _("validation failed!")
        raise serializers.ValidationError(msg)
    """


class GroupUpdateSerializer(serializers.Serializer):
    group_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True, allow_blank=False)
    pi = serializers.RegexField(regex=r'^\w+$', required=True, allow_blank=True, max_length=50)
    pi_fullname = serializers.CharField(required=False, allow_blank=True, max_length=100)
    photo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True, max_length=150)
    telephone = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=20)
    department = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=150)

