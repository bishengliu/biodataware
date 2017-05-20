from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from samples.models import SampleAttachment, SampleResearcher, SampleTissue, Sample
from django.core.validators import MinValueValidator
from api.groups.serializers import GroupSerializer, GroupResearcherSerializer
from api.users.serializers import UserSerializer


class BoxResearcherSerializer(serializers.ModelSerializer):
    researcher = GroupResearcherSerializer()

    class Meta:
        model = BoxResearcher
        fields = ('pk', 'researcher',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('pk', 'group_name', 'pi', 'pi_fullname', 'photo', 'photo_tag', 'email', 'telephone', 'department')


class GroupContainerSerializer(serializers.ModelSerializer):
    # group = serializers.StringRelatedField()
    group = GroupSerializer()
    class Meta:
        model = GroupContainer
        fields = ('pk', 'group', )


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


class ContainerUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Container
        fields = ('name', 'room', 'photo', 'temperature', 'tower', 'shelf',
                  'box', 'description')

    # need to validate the tower, shelf and box
    def validate_tower(self, value):
        try:
            boxes = BoxContainer.objects.all().filter(container_id=self.initial_data['pk'])
        except:
            msg = _("Validation of the total number of towers failed!")
            raise serializers.ValidationError(msg)
        if boxes:
            box = boxes.aggregate(Max('tower'))
            if value < box.get('tower__max'):
                msg = _("The total number of towers must not be smaller than " + str(box.get('tower__max')) + "!")
                raise serializers.ValidationError(msg)
            return value
        return value

    def validate_shelf(self, value):
        try:
            boxes = BoxContainer.objects.all().filter(container_id=self.initial_data['pk'])
        except:
            msg = _("Validation of the total number of shelves failed!")
            raise serializers.ValidationError(msg)
        if boxes:
            box = boxes.aggregate(Max('shelf'))
            if value < box.get('shelf__max'):
                msg = ("The total number of shelves must not be smaller than " + str(box.get('shelf__max')) + "!")
                raise serializers.ValidationError(msg)
            return value
        return value

    def validate_box(self, value):
        try:
            boxes = BoxContainer.objects.all().filter(container_id=self.initial_data['pk'])
        except:
            msg = _("Validation of the total number of boxes failed!")
            raise serializers.ValidationError(msg)
        if boxes:
            box = boxes.aggregate(Max('box'))
            if value < box.get('box__max'):
                msg = _("The total number of boxes must not be smaller than " + str(box.get('box__max')) + "!")
                raise serializers.ValidationError(msg)
            return value
        return value


class ContainerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Container
        fields = ('name', 'room', 'photo', 'temperature', 'tower', 'shelf',
                  'box', 'description')


class GroupContainerCreateSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField(read_only=False)
    container_id = serializers.IntegerField(read_only=False)

    class Meta:
        model = GroupContainer
        fields = ('group_id', 'container_id')

    # need to check the unique
    def validate(self, data):
        try:
            group_id = data.get('group_id')
            container_id = data.get('container_id')
            group_containers = GroupContainer.objects.all().filter(group_id=group_id).filter(container_id=container_id)
            if group_containers:
                raise serializers.ValidationError(_('Container already assigned to group, '
                                                    '\You cannot assign to the group again!'))
            return data
        except:
            msg = _("Something went wrong, the container was not assigned to the target researcher group")
            raise serializers.ValidationError(msg)


class TowerSerializer(serializers.Serializer):
    container_pk = serializers.IntegerField()
    tower_id = serializers.IntegerField()
    shelf_total = serializers.IntegerField()


class BoxContainerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BoxContainer
        fields = ('box_vertical', 'box_horizontal', 'box')


class ContainerBoxCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxContainer
        fields = ('tower', 'shelf', 'box_vertical', 'box_horizontal', 'box')


# ======for sample =====================
class SampleAttachmentSerializer(serializers.ModelSerializer):
    #sample = serializers.StringRelatedField()

    class Meta:
        model = SampleAttachment
        fields = ('pk', 'label', 'attachment', 'description', 'sample_id')


class SampleTissueSerializer(serializers.ModelSerializer):
    system = serializers.StringRelatedField()
    tissue = serializers.StringRelatedField()
    sample = serializers.StringRelatedField()

    class Meta:
        model = SampleAttachment
        fields = ('pk', 'system', 'tissue', 'sample')


class SampleResearcherSerializer(serializers.ModelSerializer):
    researcher = serializers.StringRelatedField()
    sample = serializers.StringRelatedField()

    class Meta:
        model = SampleResearcher
        fields = ('pk', 'researcher', 'sample')


class SampleSerializer(serializers.ModelSerializer):
    box = serializers.StringRelatedField()
    attachments = SampleAttachmentSerializer(many=True, read_only=True, source='sampleattachment_set')
    tissues = SampleTissueSerializer(many=True, read_only=True, source='sampletissue_set')
    researchers = SampleResearcherSerializer(many=True, read_only=True, source='sampleresearcher_set')

    class Meta:
        model = Sample
        fields = ('pk', 'vposition', 'hposition', 'position', 'date_in', 'name', 'freezing_date', 'registration_code', 'pathology_code', 'freezing_code', 'quantity', 'description', 'code39', 'qrcode', 'box', 'box_id', 'date_out', 'occupied', 'type', 'color', 'attachments', 'tissues', 'researchers')


class BoxSamplesSerializer(serializers.ModelSerializer):
    researchers = BoxResearcherSerializer(many=True, read_only=True, source='boxresearcher_set')
    samples = SampleSerializer(many=True, read_only=True, source='sample_set')

    class Meta:
        model = BoxContainer
        fields = ('pk', 'box_position', 'box_vertical', 'box_horizontal', 'tower', 'shelf', 'box', 'code39', 'qrcode', 'samples', 'researchers')


# sample color
class SampleColorSerializer(serializers.Serializer):
    color = serializers.RegexField(regex=r'^#[0-9a-fA-F]{6}$', required=True)


# add a new sample
class SampleCreateSerializer(serializers.Serializer):
    hposition = serializers.RegexField(regex=r'^[0-9]{1,2}$', required=True)  # h position
    vposition = serializers.RegexField(regex=r'^[a-zA-Z]$', required=True)  # v position
    color = serializers.RegexField(regex=r'^#[0-9a-fA-F]{6}$', required=False)  # color of the position
    name = serializers.CharField(max_length=150)  # sample
    freezing_date = serializers.DateField()  # sample freezing date
    registration_code = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)  # sample registration code, such as promas barcode
    pathology_code = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)  # sample pathology code
    freezing_code = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)  # sample freezing code
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)], default=1)  # sample quantity
    type = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)  # sample type, such as tumor
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # attachment only one file is allowed
    label = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # attachment label
    attachment = serializers.FileField(required=False, allow_null=True, allow_empty_file=True, max_length=100)
    attachment_description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # tissues
    system = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # 1-2
    tissue = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # 2,4,5-2,3,4

    # researcher
    researcher = serializers.CharField(required=False, allow_null=True, allow_blank=True) # 1,2,3


# edit sample info
class SampleEditSerializer(serializers.Serializer):
    color = serializers.RegexField(regex=r'^#[0-9a-fA-F]{6}$', required=False)  # color of the position
    name = serializers.CharField(max_length=150)  # sample
    freezing_date = serializers.DateField()  # sample freezing date
    registration_code = serializers.CharField(max_length=50, required=False, allow_null=True,
                                              allow_blank=True)  # sample registration code, such as promas barcode
    pathology_code = serializers.CharField(max_length=50, required=False, allow_null=True,
                                           allow_blank=True)  # sample pathology code
    freezing_code = serializers.CharField(max_length=50, required=False, allow_null=True,
                                          allow_blank=True)  # sample freezing code
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)], default=1)  # sample quantity
    type = serializers.CharField(max_length=200, required=False, allow_null=True,
                                 allow_blank=True)  # sample type, such as tumor
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # tissues
    system = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # 1-2
    tissue = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # 2,4,5-2,3,4

    # researcher
    researcher = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # 1,2,3


# edit sample attachment
class SampleAttachmentEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = SampleAttachment
        fields = ('label', 'attachment', 'description')

