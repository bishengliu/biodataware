from django.db import models
from users.models import User
from containers.models import BoxContainer
from django.core.validators import MinValueValidator


# bio-system model
class Biosystem(models.Model):
    system = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.system


# bio tissue
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
    occupied = forms.BooleanField(initial=True, null=True, blank=True)  # default to be true, change to false when taking out
    date_in = models.DateField(auto_now_add=True)  # timestamp
    date_out = models.DateField(widget=forms.HiddenInput(), null=True, blank=True)  # timestamp for taking the sample out
    # sample info
    name = models.CharField(max_length=150)  # sample
    freezing_date = models.DateField()  # sample freezing date
    registration_code = models.CharField(max_length=50, null=True, blank=True)  # sample registration code, such as promas barcode
    pathology_code = models.CharField(max_length=50, null=True, blank=True)  # sample pathology code
    freezing_code = models.CharField(max_length=50, null=True, blank=True)  # sample freezing code
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)  # sample quantity
    description = models.TextField(null=True, blank=True)
    code39 = models.CharField(max_length=50, null=True, blank=True)  # sample
    qrcode = models.CharField(max_length=50, null=True, blank=True)  # sample

    def __str__(self):
        return self.name + ' (Box: ' + str(self.box.tower) + '-' + str(self.box.shelf) + '-' + str(self.box.box) + ', Position: ' + self.vposition + self.hposition + ')'


# sample attachment
class SampleAttachment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    label = models.CharField(max_length=150)  # attachment label
    attachment = models.FileField(upload_to='samples/', max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.sample.name + ' :' + self.label


# sample to tissue
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
