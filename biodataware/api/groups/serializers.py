from rest_framework import serializers
from groups.models import Group, GroupResearcher, Assistant
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
