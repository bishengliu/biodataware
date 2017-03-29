from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from helpers.validators import validate_phone
from roles.models import Role


class User(AbstractUser):
    def __str__(self):
        return self.username


# extend the user model using one-to-one link
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='users/', max_length=100, null=True, blank=True)
    telephone = models.CharField(validators=[validate_phone], null=True, blank=True, max_length=20)

    # display photo in the admin
    def photo_tag(self):
        if self.photo:
            return mark_safe(settings.PHOTO_HTML % self.photo)
        else:
            return ''

    def __str__(self):
        return self.user.username


# match users to roles
class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + ' :' + self.role.role
