from django.db import models
from helpers.validators import validate_phone
from django.utils.safestring import mark_safe
from users.models import User, UserRole
from roles.models import Role
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver


class Group(models.Model):
    group_name = models.CharField(max_length=100, unique=True)
    pi = models.CharField(max_length=100)
    pi_fullname = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='groups/', max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=50, unique=True)
    telephone = models.CharField(validators=[validate_phone], null=True, blank=True, max_length=20)
    department = models.CharField(max_length=150, null=True, blank=True)

    # display photo in the admin
    def photo_tag(self):
        if self.photo:
            return mark_safe(settings.PHOTO_HTML % self.photo)
        else:
            return ''

    photo_tag.short_description = 'Photo'
    photo_tag.allow_tags = True

    def __str__(self):
        return self.group_name + " (" + self.pi + ")"


# auto create user PI role
@receiver(post_save, sender=Group)
def auto_set_PI(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    group_email = instance.email
    # check for user
    user = User.objects.all().filter(email__iexact=group_email).first()
    if user is not None:
        # check PI role
        pi_role = Role.objects.all().filter(role__exact='PI').first()
        if pi_role is not None:
            # create PI role of the user
            user_role = UserRole.objects.create(
                user_id=user.pk,
                role_id=pi_role.pk)
            user_role.save()
            # add user to the group
    group_researcher = GroupResearcher.objects.all().filter(group_id=instance.pk).filter(user_id=user.pk).first()
    if group_researcher is None:
        researcher = GroupResearcher.objects.create(
            user_id=user.pk,
            group_id=instance.pk)
        researcher.save()


# auto remove user pi role
@receiver(post_delete, sender=Group)
def auto_remove_PI(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    group_email = instance.email
    # check for user
    user = User.objects.all().filter(email__iexact=group_email).first()
    if user is not None:
        # check user role
        pi_userrole = UserRole.objects.all().filter(user_id=user.pk).first()
        if pi_userrole is not None:
            # check Assistant and Group Researcher
            assistants = Assistant.objects.all().filter(group_id=instance.pk)
            groupresearchers = GroupResearcher.objects.all().filter(group_id=instance.pk).exclude(user_id=user.pk)
            if not assistants and not groupresearchers:
                pi_userrole.delete()
            # delete selt in groupresearcher
            groupresearcher = GroupResearcher.objects.all().filter(group_id=instance.pk).filter(user_id=user.pk).first()
            if groupresearcher is not None:
                groupresearcher.delete()


# admin assistants
class Assistant(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.pi + " (" + self.user.email + ")"


# researchers in the group
class GroupResearcher(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.group_name + " (" + self.group.pi + ")"
