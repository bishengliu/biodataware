from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from csamples.models import CSampleAttachment, CSampleResearcher, CSample
from django.core.validators import MinValueValidator
from api.groups.serializers import GroupSerializer, GroupResearcherSerializer
from api.users.serializers import UserSerializer
from api.ctypes.serializers import *
from django.core.validators import MaxValueValidator, MinValueValidator


class CSampleDataSerializer(serializers.ModelSerializer):
    ctype_attr = CTypeAttrSerializer()

    class Meta:
        model = CSampleData
        fields = ('pk', 'csample_id', 'ctype_attr_id', 'ctype_attr', 'ctype_attr_value_part1', 'ctype_attr_value_part2')


class CSampleSubDataSerializer(serializers.ModelSerializer):
    ctype_sub_attr = CTypeSubAttrSerializer()

    class Meta:
        model = CSampleData
        fields = ('pk', 'csample_id', 'ctype_sub_attr_id', 'ctype_sub_attr', 'ctype_sub_attr_value_part1', 'ctype_sub_attr_value_part2')


class CSampleAttachmentSerializer(serializers.ModelSerializer):
    # sample = serializers.StringRelatedField()

    class Meta:
        model = CSampleAttachment
        fields = ('pk', 'label', 'attachment', 'description', 'sample_id')


class CSampleSerializer(serializers.ModelSerializer):
    box = serializers.StringRelatedField()
    attachments = CSampleAttachmentSerializer(many=True, read_only=True, source='sampleattachment_set')
    researchers = UserSerializer(many=True, read_only=True, source='researcher_objs')
    ctype = CTypeSerializer()
    csample_data = CSampleDataSerializer(many=True, read_only=True, source='csampledata_set')
    cample_subdata = CSampleSubDataSerializer(many=True, read_only=True, source='csamplesubdata_set')

    class Meta:
        model = CSample
        fields = ('pk', 'ctype_id', 'vposition', 'hposition', 'position', 'date_in', 'name', 'storage_date',
                  'box', 'box_id', 'date_out', 'occupied', 'color', 'attachments', 'ctype', 'csample_data', 'cample_subdata',
                  'researchers', 'container_id', 'container', 'box_position')


class BoxCSamplesSerializer(serializers.ModelSerializer):
    researchers = UserSerializer(many=True, read_only=True, source='researcher_objs')
    # researchers = BoxResearcherSerializer(many=True, read_only=True, source='boxresearcher_set')
    csamples = CSampleSerializer(many=True, read_only=True, source='csample_set')

    class Meta:
        model = BoxContainer
        fields = ('pk', 'label', 'box_position', 'box_vertical', 'box_horizontal', 'tower', 'shelf', 'box',
                  'code39', 'qrcode', 'color', 'rate', 'description', 'csamples', 'sample_count', 'researchers')
