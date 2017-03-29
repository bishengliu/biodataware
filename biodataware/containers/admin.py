from django.contrib import admin
from .models import Container, GroupContainer, BoxContainer, BoxResearcher


# Register Container
class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo_tag', 'room', 'code39', 'qrcode', 'temperature', 'tower', 'shelf', 'box', 'description']

admin.site.register(Container, ContainerAdmin)


# register ContainerBox
class ContainerBoxAdmin(admin.ModelAdmin):
    list_display = ['container', 'temperature', 'room', 'position', 'dimension', 'code39', 'qrcode']

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
            return obj.container.name + ' (' + str(obj.tower) + '-' + str(obj.shelf) + '-' + str(obj.box) + ')'
        except:
            return None

    position.short_description = 'Box'

    def dimension(self, obj):
        try:
            return str(obj.box_vertical) + 'x' + str(obj.box_horizontal)
        except:
            return None

    dimension.short_description = 'Dimension'

    def room(self, obj):
        try:
            return obj.container.room
        except:
            return None

    room.short_description = 'Room'

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

admin.site.register(BoxContainer, ContainerBoxAdmin)


# register group container
class GroupContainerAdmin(admin.ModelAdmin):
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

    room.short_description = 'Room'

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

admin.site.register(GroupContainer, GroupContainerAdmin)


# register boxes for register
class BoxResearcherAdmin(admin.ModelAdmin):
    list_display = ['position', 'freezer', 'temperature', 'room', 'researcher', 'email', 'group', 'code39', 'qrcode']

    def position(self, obj):
        try:
            return obj.box.container.name + ' (' + str(obj.box.tower) + '-' + str(obj.box.shelf) + '-' + str(obj.box.box) + ')'
        except:
            return None

    position.short_description = 'Box'

    def freezer(self, obj):
        try:
            return obj.box.container.name
        except:
            return None

    freezer.short_description = 'Freezer'

    def temperature(self, obj):
        try:
            return obj.box.container.temperature
        except:
            return None

    temperature.short_description = 'Temperature'

    def room(self, obj):
        try:
            return obj.box.container.room
        except:
            return None

    room.short_description = 'Room'

    def researcher(self, obj):
        try:
            return obj.researcher.user.username
        except:
            return None

    researcher.short_description = 'Researcher'

    def email(self, obj):
        try:
            return obj.researcher.user.email
        except:
            return None

    email.short_description = 'Email'

    def group(self, obj):
        try:
            return obj.researcher.group.group_name
        except:
            return None

    group.short_description = 'Group'

    def code39(self, obj):
        try:
            return obj.box.code39
        except:
            return None

    code39.short_description = 'Code39'

    def qrcode(self, obj):
        try:
            return obj.box.qrcode
        except:
            return None

    qrcode.short_description = 'QRCode'

admin.site.register(BoxResearcher, BoxResearcherAdmin)
