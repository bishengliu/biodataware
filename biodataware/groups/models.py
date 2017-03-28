from django.db import models
from helpers.validators import validate_phone
from django.utils.safestring import mark_safe
from users.models import User


class Group(models.Model):
    group_name = models.CharField(max_length=100, unique=True)
    pi = models.CharField(max_length=100)
    pi_fullname = models.CharField(max_length=150, null=True, blank=True)
    photo = models.ImageField(upload_to='groups/', max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    telephone = models.CharField(validators=[validate_phone], null=True, blank=True, max_length=20)
    department = models.CharField(max_length=150, null=True, blank=True)

    # display photo in the admin
    def photo_tag(self):
        if self.photo:
            return mark_safe('<img src="/media/%s" width="50" height="50" />' % self.photo)
        else:
            return ''

    def __str__(self):
        return self.group_name + " (" + self.pi + ")"


# admin assistants
class Assistant(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.pi + " (" + self.user.email + ")"


# researchers in the group
class GroupResearcher(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.pi + " (" + self.user.email + ")"
