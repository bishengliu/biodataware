from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from samples.models import SampleAttachment, SampleResearcher, SampleTissue, Sample, SampleTag
from django.core.validators import MinValueValidator
from api.groups.serializers import GroupSerializer, GroupResearcherSerializer
from api.users.serializers import UserSerializer
from django.core.validators import MaxValueValidator, MinValueValidator


class BoxResearcherSerializer(serializers.ModelSerializer):
    researcher = UserSerializer(source='user', many=False, read_only=True)

    class Meta:
        model = BoxResearcher
        fields = ('pk', 'researcher',)


class GroupContainerSerializer(serializers.ModelSerializer):
    # group = serializers.StringRelatedField()
    group = GroupSerializer()

    class Meta:
        model = GroupContainer
        fields = ('pk', 'group', )


# load boxes without loading the samples
class BoxContainerSerializer(serializers.ModelSerializer):
    # researchers = BoxResearcherSerializer(many=True, read_only=True, source='boxresearcher_set')
    researchers = UserSerializer(many=True, read_only=True, source='researcher_objs')

    class Meta:
        model = BoxContainer
        fields = ('pk', 'label', 'box_position', 'box_vertical', 'box_horizontal', 'tower', 'shelf', 'box', 'code39', 'qrcode', 'color', 'rate', 'description', 'researchers')


class ContainerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
        fields = ('pk', 'name', 'room', 'photo',  'temperature', 'tower', 'shelf',
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
        fields = ('box_vertical', 'box_horizontal', 'box', 'color', 'description')


class ContainerBoxCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxContainer
        fields = ('tower', 'shelf', 'box_vertical', 'box_horizontal', 'box', 'color', 'description')


# ======for sample =====================
class SampleAttachmentSerializer(serializers.ModelSerializer):
    #sample = serializers.StringRelatedField()

    class Meta:
        model = SampleAttachment
        fields = ('pk', 'label', 'attachment', 'description', 'sample_id')


class SampleTissueSerializer(serializers.ModelSerializer):
    system = serializers.StringRelatedField()
    tissue = serializers.StringRelatedField()
    # sample = serializers.StringRelatedField()

    class Meta:
        model = SampleTissue
        fields = ('pk', 'system', 'tissue', 'sample_id')


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
    # researchers = SampleResearcherSerializer(many=True, read_only=True, source='sampleresearcher_set')
    researchers = UserSerializer(many=True, read_only=True, source='researcher_objs')

    class Meta:
        model = Sample
        fields = ('pk', 'vposition', 'hposition', 'position', 'date_in', 'name', 'freezing_date',
                  'registration_code', 'pathology_code', 'freezing_code', 'quantity', 'description',
                  'code39', 'qrcode', 'box', 'box_id', 'date_out', 'occupied', 'type', 'color', 'attachments',
                  'tissues', 'researchers',
                  'label', 'tag', 'official_name', 'quantity_unit', 'reference_code', 'oligo_name', 's_or_as',
                  'oligo_sequence', 'oligo_length', 'oligo_GC', 'target_sequence', 'clone_number', 'against_260_280',
                  'feature', 'r_e_analysis', 'backbone', 'insert', 'first_max', 'marker', 'has_glycerol_stock',
                  'strain', 'passage_number', 'cell_amount', 'project', 'creator', 'plasmid', 'titration_titer',
                  'titration_unit', 'titration_cell_type', 'titration_code')


class BoxSamplesSerializer(serializers.ModelSerializer):
    researchers = UserSerializer(many=True, read_only=True, source='researcher_objs')
    # researchers = BoxResearcherSerializer(many=True, read_only=True, source='boxresearcher_set')
    samples = SampleSerializer(many=True, read_only=True, source='sample_set')

    class Meta:
        model = BoxContainer
        fields = ('pk', 'label', 'box_position', 'box_vertical', 'box_horizontal', 'tower', 'shelf', 'box', 'code39', 'qrcode', 'color', 'rate', 'description', 'samples', 'researchers')


class ConatainerSerializer(serializers.ModelSerializer):
    # groups = GroupContainerSerializer(many=True, read_only=True, source='groupcontainer_set')
    groups = GroupSerializer(many=True, read_only=True, source='group_objs')

    # boxes no samples
    boxes = BoxContainerSerializer(many=True, read_only=True, source='boxcontainer_set')

    # boxes with samples
    # boxes = BoxSamplesSerializer(many=True, read_only=True, source='boxcontainer_set')

    class Meta:
        model = Container
        fields = ('pk', 'name', 'room', 'photo', 'photo_tag', 'temperature', 'code39', 'qrcode', 'tower', 'shelf',
                      'box', 'description', 'groups', 'boxes')


# sample color
class SampleColorSerializer(serializers.Serializer):
    color = serializers.RegexField(regex=r'^#[0-9a-fA-F]{6}$', required=True)


# box color
class BoxColorSerializer(serializers.Serializer):
    color = serializers.RegexField(regex=r'^#[0-9a-fA-F]{6}$', required=True)


# box rate
class BoxRateSerializer(serializers.Serializer):
    rate = serializers.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], required=True)


# update description
class BoxDescriptionSerializer(serializers.Serializer):
    description = serializers.CharField(required=False)


# box label
class BoxLabelSerializer(serializers.Serializer):
    label = serializers.CharField(required=False)


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


# move boxes
class MoveBoxSerializer(serializers.Serializer):
    original_container = serializers.IntegerField(required=True)  # original_container pk
    box_full_position = serializers.CharField(required=True)  # box_full_position
    target_container = serializers.IntegerField(required=True)  # target_container pk
    target_box_full_position = serializers.CharField(required=True)  # target_container box_full_position


# add a box to a container
class AddBoxSerializer(serializers.Serializer):
    container_pk = serializers.IntegerField(required=True)  # container pk
    box_full_position = serializers.CharField(required=True)  # box_full_position
    box_horizontal = serializers.IntegerField(validators=[MinValueValidator(1)], required=True)  # box_horizontal
    box_vertical = serializers.IntegerField(validators=[MinValueValidator(1)], required=True)  # box_vertical


# switch sample position
class SwitchSampleSerializer(serializers.Serializer):
    box_full_position = serializers.CharField(required=True)  # box_full_position
    first_sample = serializers.CharField(required=True)  # box_full_position
    second_sample = serializers.CharField(required=True)  # box_full_position


# switch samples between 2 boxes
class SwitchSampleBoxesSerializer(serializers.Serializer):
    first_container_pk = serializers.IntegerField(required=True)  # first container pk
    first_box_tower = serializers.IntegerField(required=True)
    first_box_shelf = serializers.IntegerField(required=True)
    first_box_box = serializers.IntegerField(required=True)
    first_sample_vposition = serializers.CharField(required=True)
    first_sample_hposition = serializers.IntegerField(required=True)
    second_container_pk = serializers.IntegerField(required=True)  # second container pk
    second_box_tower = serializers.IntegerField(required=True)
    second_box_shelf = serializers.IntegerField(required=True)
    second_box_box = serializers.IntegerField(required=True)
    second_sample_vposition = serializers.CharField(required=True)
    second_sample_hposition = serializers.IntegerField(required=True)


# sample tags
class SampleTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = SampleTag
        fields = ('name', 'category', 'group_id')
