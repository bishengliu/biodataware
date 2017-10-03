from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from groups.models import Group, GroupResearcher
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth import get_user_model

# containers
class Container(models.Model):
    name = models.CharField(max_length=100, unique=True)
    room = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='containers/', max_length=150, null=True, blank=True)
    code39 = models.CharField(max_length=50, null=True, blank=True)
    qrcode = models.CharField(max_length=50, null=True, blank=True)
    temperature = models.CharField(max_length=50, null=True, blank=True)
    tower = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    shelf = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    box = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    description = models.TextField(null=True, blank=True)

    # display photo in the admin
    def photo_tag(self):
        if self.photo:
            return mark_safe(settings.PHOTO_HTML % self.photo)
        else:
            return ''

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def __str__(self):
        return self.name

    def group_objs(self):
        gc_set = self.groupcontainer_set
        if gc_set:
            group_ids = []
            for x in gc_set.values('group'):
                group_ids.append(x['group'])
            if group_ids:
                groups = Group.objects.all().filter(pk__in=group_ids)
                return groups
        return None

    def has_box(self):
        if self.boxcontainer_set is not None and self.boxcontainer_set.count() > 0:
            return True
        return False


# containers to groups
class GroupContainer(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    def __str__(self):
        return self.container.name + ' (' + self.group.group_name + ')'


# boxes in containers
class BoxContainer(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, null=True, blank=True)  # user defined position or label
    code39 = models.CharField(max_length=50, null=True, blank=True)
    qrcode = models.CharField(max_length=50, null=True, blank=True)
    tower = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    shelf = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    box = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    box_vertical = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], default=8)   # A-H
    box_horizontal = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], default=8)  # 1-8
    color = models.CharField(max_length=20, null=True, blank=True)  # color of the position
    rate = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def box_position(self):
        return str(self.tower) + '-' + str(self.shelf) + '-' + str(self.box)

    def __str__(self):
        return self.container.name + ' (' + str(self.tower) + '-' + str(self.shelf) + '-' + str(self.box) + ')'

    def researcher_objs(self):
        br_set = self.boxresearcher_set
        if br_set:
            user_ids = []
            for u in br_set.values('researcher'):
                user_ids.append(u['researcher'])
            if user_ids:
                User = get_user_model()
                users = User.objects.all().filter(pk__in=user_ids)
                return users
        return None

# boxes assigned to the group
class BoxResearcher(models.Model):
    box = models.ForeignKey(BoxContainer, on_delete=models.CASCADE)
    researcher = models.ForeignKey(GroupResearcher, on_delete=models.CASCADE)

    def user(self):
        return self.researcher.user

    def __str__(self):
        return self.box.container.name + ' (' + str(self.box.tower) + '-' + str(self.box.shelf) + '-' + str(self.box.box) + ') of researcher: ' + self.researcher.user.username