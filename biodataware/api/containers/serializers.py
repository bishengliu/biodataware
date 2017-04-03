from rest_framework import serializers
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher


class BoxResearcherSerializer(serializers.ModelSerializer):

    class Meta:
        model = BoxResearcher
        fields = ('researcher_id', 'researcher_name', 'researcher_email', )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('pk', 'group_name', 'pi', 'pi_fullname', 'photo', 'photo_tag', 'email', 'telephone', 'department')


class GroupContainerSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField()

    class Meta:
        model = GroupContainer
        fields = ('group_id', 'group')


class BoxContainerSerializer(serializers.ModelSerializer):

    researchers = BoxResearcherSerializer(many=True, read_only=True, source='boxresearcher_set')

    class Meta:
        model = BoxContainer
        fields = ('pk', 'box_position', 'box_vertical', 'box_horizontal', 'tower', 'shelf', 'box', 'code39', 'qrcode', 'researchers')


class ConatainerSerializer(serializers.ModelSerializer):
    groups = GroupContainerSerializer(many=True, read_only=True, source='groupcontainer_set')
    boxes = BoxContainerSerializer(many=True, read_only=True, source='boxcontainer_set')

    class Meta:
        model = Container
        fields = ('pk', 'name', 'room', 'photo', 'photo_tag', 'temperature', 'code39', 'qrcode', 'tower', 'shelf',
                  'box', 'description', 'groups', 'boxes')


class ContainerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Container
        fields = ('name', 'room', 'photo', 'temperature', 'tower', 'shelf',
                  'box', 'description')
