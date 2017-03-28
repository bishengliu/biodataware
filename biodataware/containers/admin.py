from django.contrib import admin
from .models import Container, GroupContainer, BoxConatiner


# Register Container
class ContainerAdmin(admin.ModelAdmin):
    list_display = ['photo', 'name', 'room', 'code39', 'qrcode', 'temperature', 'tower', 'shelf', 'box', 'box_vertical', 'box_horizontal', 'description']

    def photo(self, obj):
        try:
            return obj.container.photo_tag()
        except:
            return None

    photo.short_description = 'Container Photo'
    photo.allow_tags = True

admin.site.register(Container, ContainerAdmin)


# register BoxConatiner
class BoxConatinerAdmin(admin.ModelAdmin):
    list_display = ['container', 'temperature', 'position', 'room', 'code39', 'qrcode']

    def container(self, obj):
        try:
            return obj.container.name
        except:
            return None

    container.short_description = 'Container'

    def temperature(self, obj):
        try:
            return obj.container.temperature
        except:
            return None

    temperature.short_description = 'Temperature'

    def position(self, obj):
        try:
            return str(obj.container.tower) + '-' + str(obj.container.shelf) + '-' + str(obj.container.box)
        except:
            return None

    position.short_description = 'Position'

    def room(self, obj):
        try:
            return obj.container.room
        except:
            return None

    temperature.short_description = 'Room'

    def code39(self, obj):
        try:
            return obj.code39
        except:
            return None

    code39.short_description = 'Code39'

    def qrcode(self, obj):
        try:
            return obj.qrcode
        except:
            return None

    qrcode.short_description = 'QRCode'


admin.site.register(BoxConatiner, BoxConatinerAdmin)


# register group container
class GroupConatinerAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'pi', 'container', 'temperature', 'room', 'code39', 'qrcode']

    def group_name(self, obj):
        try:
            return obj.group.group_name
        except:
            return None

    group_name.short_description = 'Group Name'

    def pi(self, obj):
        try:
            return obj.group.pi
        except:
            return None

    pi.short_description = 'PI'

    def container(self, obj):
        try:
            return obj.container.name
        except:
            return None

    container.short_description = 'Container'

    def temperature(self, obj):
        try:
            return obj.container.temperature
        except:
            return None

    temperature.short_description = 'Temperature'

    def room(self, obj):
        try:
            return obj.container.room
        except:
            return None

    temperature.short_description = 'Room'

    def code39(self, obj):
        try:
            return obj.container.code39
        except:
            return None

    code39.short_description = 'Code39'

    def qrcode(self, obj):
        try:
            return obj.container.qrcode
        except:
            return None

    qrcode.short_description = 'QRCode'

admin.site.register(GroupContainer, GroupConatinerAdmin)
