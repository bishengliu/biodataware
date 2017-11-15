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


# bio-system model, not used anymore
class Biosystem(models.Model):
    system = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.system


# bio tissue, not used anymore
class Tissue(models.Model):
    tissue = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.tissue


# Sample model
class Sample(models.Model):
    # link to the box
    box = models.ForeignKey(BoxContainer, on_delete=models.CASCADE)
    hposition = models.CharField(max_length=10)  # h position
    vposition = models.CharField(max_length=10)  # v position
    occupied = models.BooleanField(default=True)  # default to be true, change to false when taking out
    color = models.CharField(max_length=20, null=True, blank=True)  # color of the position
    date_in = models.DateField()  # timestamp, auto_now_add=True
    date_out = models.DateField(null=True, blank=True)  # timestamp for taking the sample out
    # sample info
    name = models.CharField(max_length=150)  # sample
    freezing_date = models.DateField(default=datetime.now, null=True, blank=True)  # sample freezing date
    registration_code = models.CharField(max_length=50, null=True, blank=True)  # sample registration code, such as promas barcode
    freezing_code = models.CharField(max_length=50, null=True, blank=True)  # sample freezing code
    # quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)  # sample quantity
    quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)  # sample quantity
    type = models.CharField(max_length=200, null=True, blank=True)  # sample type, such as tumor
    description = models.TextField(null=True, blank=True)
    code39 = models.CharField(max_length=50, null=True, blank=True)  # sample
    qrcode = models.CharField(max_length=50, null=True, blank=True)  # sample

    # tissue only
    pathology_code = models.CharField(max_length=50, null=True, blank=True)  # sample pathology code
    tissue = models.CharField(max_length=50, null=True, blank=True)  # sample

    # extra attrs for molecular lab
    label = models.CharField(max_length=50, null=True, blank=True)
    tag = models.CharField(max_length=50, null=True, blank=True)
    official_name = models.CharField(max_length=100, null=True, blank=True)
    quantity_unit = models.CharField(max_length=50, null=True, blank=True)
    reference_code = models.CharField(max_length=50, null=True, blank=True)

    # (gRNA) Oligo only
    oligo_name = models.CharField(max_length=100, null=True, blank=True)
    s_or_as = models.NullBooleanField()  # sense or antisense
    oligo_sequence = models.CharField(max_length=100, null=True, blank=True)
    oligo_length = models.IntegerField(validators=[MinValueValidator(100)], null=True, blank=True)  # sample quantity
    oligo_GC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_sequence = models.CharField(max_length=100, null=True, blank=True)

    # construct only
    clone_number = models.CharField(max_length=50, null=True, blank=True)
    against_260_280 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    feature = models.CharField(max_length=150, null=True, blank=True)
    r_e_analysis = models.CharField(max_length=50, null=True, blank=True)
    backbone = models.CharField(max_length=50, null=True, blank=True)
    insert = models.CharField(max_length=50, null=True, blank=True)
    first_max = models.CharField(max_length=50, null=True, blank=True)
    marker = models.CharField(max_length=100, null=True, blank=True)
    has_glycerol_stock = models.CharField(max_length=50, null=True, blank=True)
    strain = models.CharField(max_length=50, null=True, blank=True)

    # cell line
    passage_number = models.CharField(max_length=50, null=True, blank=True)
    cell_amount = models.CharField(max_length=50, null=True, blank=True)
    project = models.CharField(max_length=50, null=True, blank=True)
    creator = models.CharField(max_length=50, null=True, blank=True)

    # virus
    plasmid = models.CharField(max_length=50, null=True, blank=True)
    titration_titer = models.CharField(max_length=50, null=True, blank=True)
    titration_unit = models.CharField(max_length=50, null=True, blank=True)
    titration_cell_type = models.CharField(max_length=50, null=True, blank=True)
    titration_code = models.CharField(max_length=50, null=True, blank=True)

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


# upload handler
def upload_path_handler(instance, filename):
    # get the sample
    sample = Sample.objects.get(pk=instance.sample_id)
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
    # attachment = models.FileField(upload_to='samples/', max_length=250, null=True, blank=True)
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


# sample to tissue, not used anymore
class SampleTissue(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    system = models.ForeignKey(Biosystem, on_delete=models.CASCADE)
    tissue = models.ForeignKey(Tissue, on_delete=models.CASCADE)

    def __str__(self):
        return self.sample.name + ' (' + self.system.system + '/' + self.tissue.tissue + ')'


# sample to researcher
class SampleResearcher(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    researcher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.sample.name + ' (' + self.researcher.username + ')'


# sample tags, not used anymore
class SampleTag(models.Model):
    name = models.CharField(max_length=50)  # attachment label
    category = models.CharField(max_length=50)  # attachment label
    group_id = models.IntegerField(null=True, blank=True) # point to groups


# sample drop downs
class SampleDropdown(models.Model):
    name = models.CharField(max_length=50)  # attachment label
    category = models.CharField(max_length=50)  # attachment label
    group_id = models.IntegerField(null=True, blank=True) # point to groups