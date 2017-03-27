from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from helpers.validators import validate_phone


class User(AbstractUser):
    def __str__(self):
        return self.username


# extend the user model using one-to-one link
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='users/', max_length=100, null=True, blank=True)
    telephone = models.CharField(validators=[validate_phone], null=True, blank=True)

    # display photo in the admin
    def photo_tag(self):
        if self.photo:
            return mark_safe('<img src="/media/%s" width="50" height="50" />' % self.photo)
        else:
            return ''

    def __str__(self):
        return self.user.username

