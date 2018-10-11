from django.db import models
from users.models import User
from containers.models import BoxContainer, Container
from django.core.validators import MinValueValidator

# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.contrib.auth import get_user_model
from datetime import datetime
import os


# sample types
class SampleType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateField(default=datetime.now, null=True, blank=True)


# sample
class Sample(models.Model):
    sample_type = models.ForeignKey(SampleType, on_delete=models.CASCADE)
    box = models.ForeignKey(BoxContainer, on_delete=models.CASCADE)
    hposition = models.CharField(max_length=10)  # h position
    vposition = models.CharField(max_length=10)  # v position
    occupied = models.BooleanField(default=True)  # default to be true, change to false when taking out
    color = models.CharField(max_length=20, null=True, blank=True)  # color of the position
    date_in = models.DateField()  # timestamp, auto_now_add=True
    date_out = models.DateField(null=True, blank=True)  # timestamp for taking the sample out
    # sample info
    name = models.CharField(max_length=150)  # sample
    storage_date = models.DateField(default=datetime.now, null=True, blank=True)  # sample storage date

    def position(self):
        return self.vposition + self.hposition

    def __str__(self):
        return self.name + ' (Box: ' + str(self.box.tower) + '-' + str(self.box.shelf) + '-' + str(self.box.box) + ', Position: ' + self.vposition + self.hposition + ')'

    def researcher_objs(self):
        sr_set = self.sampleresearcher_set
        if sr_set:
            user_ids = []
            for u in sr_set.values('researcher'):
                user_ids.append(u['researcher'])
            if user_ids:
                User = get_user_model()
                users = User.objects.all().filter(pk__in=user_ids)
                return users
        return None

    def container_id(self):
        return self.box.container_id

    def container(self):
        return self.box.container.name

    def box_position(self):
        return str(self.box.tower) + '-' + str(self.box.shelf) + '-' + str(self.box.box)


# minimal sample attr for all types, see above
class SampleMinimalAttr(models.Model):
    attr_required = models.BooleanField(default=True)
    attr_name = models.CharField(max_length=130)
    attr_label = models.CharField(max_length=130)
    attr_value_type = models.CharField(max_length=130)  # 0: string, 1, digit; 2, decimal
    attr_value_text_max_length = models.IntegerField(validators=[MinValueValidator(0)], null=True,
                                                     blank=True)  # only for string or text field
    attr_value_decimal_total_digit = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    attr_value_decimal_point = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)


# sample top extra attrs
class SampleAttr(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    attr_name = models.CharField(max_length=130)
    attr_label = models.CharField(max_length=130)
    attr_value_type = models.CharField(max_length=130)  # 0: string, 1, digit; 2, decimal
    attr_value_text_max_length = models.IntegerField(validators=[MinValueValidator(0)], null=True,
                                                     blank=True)  # only for string or text field
    attr_value_decimal_total_digit = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    attr_value_decimal_point = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    attr_required = models.BooleanField(default=False)
    attr_order = models.IntegerField()
    has_sub_attr = models.BooleanField(default=False)


# sample sub attrs
class SampleSubAttr(models.Model):
    parent_attr = models.ForeignKey(SampleAttr, on_delete=models.CASCADE)
    attr_name = models.CharField(max_length=130)
    attr_label = models.CharField(max_length=130)
    attr_value_type = models.CharField(max_length=130)  # 0: string, 1, digit; 2, decimal
    attr_value_text_max_length = models.IntegerField(validators=[MinValueValidator(0)], null=True,
                                                     blank=True)  # only for string or text field
    attr_value_decimal_total_digit = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    attr_value_decimal_point = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    attr_required = models.BooleanField(default=False)
    attr_order = models.IntegerField()


# sample data match attrs
class SampleData(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    sample_attr = models.ForeignKey(SampleAttr, on_delete=models.CASCADE)
    sample_sub_attr_value_part1 = models.TextField(null=True, blank=True)
    sample_sub_attr_value_part2 = models.TextField(null=True, blank=True)


# sample subdata match sub attrs
class SampleSubData(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    sample_sub_attr = models.ForeignKey(SampleSubAttr, on_delete=models.CASCADE)
    sample_sub_attr_value_part1 = models.TextField(null=True, blank=True)
    sample_sub_attr_value_part2 = models.TextField(null=True, blank=True)


# upload handler
def upload_path_handler(instance, filename):
    # get the sample data
    sample = SampleData.objects.get(pk=instance.sample_id)
    if sample is not None:
        # get the box
        box = BoxContainer.objects.get(pk=sample.box_id)
        if box is not None:
            # get the container
            container = Container.objects.get(pk=box.container_id)
            if container is not None:
                # new file name
                format_filename = 'sample_' + str(sample.pk) + '_' + filename
                return os.path.join('samples', 'container_' + str(container.pk), format_filename)
    return os.path.join('samples', filename)


# sample attachment
class SampleAttachment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    label = models.CharField(max_length=150)  # attachment label
    attachment = models.FileField(upload_to=upload_path_handler, max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.sample.name + ' :' + self.label

    def filename(self):
        return os.path.basename(self.file.name)


@receiver(pre_delete, sender=SampleAttachment)
def sample_attachment_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.attachment:
        instance.attachment.delete(False)


# only for viruses
class SampleVirusTitration(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    titration_titer = models.CharField(max_length=50, null=True, blank=True)
    titration_unit = models.CharField(max_length=50, null=True, blank=True)
    titration_cell_type = models.CharField(max_length=50, null=True, blank=True)
    titration_code = models.CharField(max_length=50, null=True, blank=True)
    titration_date = models.DateField(default=datetime.now, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.titration_titer + self.titration_unit + ' (' + self.titration_date + ')'


# sample to researcher
class SampleResearcher(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    researcher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.researcher.username
