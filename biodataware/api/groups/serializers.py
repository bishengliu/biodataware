from rest_framework import serializers
from groups.models import Group, GroupResearcher, Assistant
from users.models import UserRole, User
from django.utils.translation import ugettext_lazy as _


# no view
class AssistantSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = GroupResearcher
        fields = ('user_id', 'user')


# no view
class GroupResearcherSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

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


class ResearcherRoleSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()

    class Meta:
        model = UserRole
        fields = ('role', )


class ResearchersSerializer(serializers.ModelSerializer):
    roles = ResearcherRoleSerializer(many=True, read_only=True, source='userrole_set')

    class Meta:
        model = User
        fields = ('pk', 'email', 'username', 'first_name', 'last_name', 'roles')


class GroupResearcherCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupResearcher
        field = ('user_id', 'group_id')

    def validated(self, data):
        if 'user_id' in data and 'group_id' in data:
            group_researcher = GroupResearcher.objects.all().filter(user_id=data['user_id']).filter(group_id=data['group_id'])
            if group_researcher:
                msg = _("Something went wrong, validation failed")
                raise serializers.ValidationError(msg)
            return data
