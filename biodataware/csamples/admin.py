from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *


class CTypeAdmin(admin.ModelAdmin):
    list_display = ['type', 'description']

    def type(self, obj):
        try:
            return obj.type
        except:
            return None

    type.short_description = 'Type'

    def description(self, obj):
        try:
            return obj.description
        except:
            return None

    description.short_description = 'Description'


admin.site.register(CType, CTypeAdmin)


class CSampleAdmin(admin.ModelAdmin):
    list_display = ['ctype', 'container', 'container_box', 'name', 'position', 'storage_date',
                    'description', 'attachment', 'researcher', 'occupied', 'date_out']

    def ctype(self, obj):
        try:
            return obj.ctype.type
        except:
            return None

    ctype.short_description = 'Type'

    def description(self, obj):
        try:
            return obj.description
        except:
            return None

    description.short_description = 'Description'

    def name(self, obj):
        try:
            return obj.name
        except:
            return None
    name.short_description = 'Name'

    def container_box(self, obj):
        try:
            return str(obj.box.tower) + '-' + str(obj.box.shelf) + '-' + str(obj.box.box)
        except:
            return None

    container_box.short_description = 'Box'

    def container(self, obj):
        try:
            return obj.box.container.name
        except:
            return None

    container.short_description = 'Container'

    def position(self, obj):
        try:
            return obj.vposition + obj.hposition
        except:
            return None

    position.short_description = 'Position'

    def attachment(self, obj):
        try:
            attachments = obj.sampleattachment_set.all()
            output = ''
            for a in attachments:
                output += '<a href="' + a.attachment.url + '" class="" alt="' + a.label + '"><i></i><span>' + a.label + '</span></a>' + '<br/>'
            return mark_safe(output)
        except:
            return None

    attachment.short_description = 'Attachment(s)'

    def researcher(self, obj):
        try:
            researchers = obj.sampleresearcher_set.all()
            output = ''
            for r in researchers:
                output += r.researcher.username + ' (' + r.researcher.email + ')' + '<br/>'
            return mark_safe(output)
        except:
            return None

    researcher.short_description = 'Researcher'

    def date_out(self, obj):
        try:
            return obj.date_out
        except:
            return None

    date_out.short_description = 'Taken Date'

    def occupied(self, obj):
        try:
            return obj.occupied
        except:
            return None

    occupied.short_description = 'Taken'

    def storage_date(self, obj):
        try:
            return obj.storage_date
        except:
            return None

    storage_date.short_description = 'Storage Date'


admin.site.register(CSample, CSampleAdmin)


class CTypeMinimalAttrAdmin(admin.ModelAdmin):
    pass


admin.site.register(CTypeMinimalAttr, CTypeMinimalAttrAdmin)


class CTypeAttrAdmin(admin.ModelAdmin):
    pass


admin.site.register(CTypeAttr, CTypeAttrAdmin)


class CTypeSubAttrAdmin(admin.ModelAdmin):
    pass


admin.site.register(CTypeSubAttr, CTypeSubAttrAdmin)


class CSampleDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(CSampleData, CSampleDataAdmin)


class CSampleSubDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(CSampleSubData, CSampleSubDataAdmin)


class CSampleVirusTitrationAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'titration_titer', 'titration_unit', 'titration_cell_type',
                    'titration_code', 'titration_date', 'description']

    def type(self, obj):
        try:
            return obj.csample.csample_type.type
        except:
            return None

    type.short_description = 'Type'

    def name(self, obj):
        try:
            return obj.csample.name
        except:
            return None

    name.short_description = 'Name'

    def titration_titer(self, obj):
        try:
            return obj.titration_titer
        except:
            return None

    titration_titer.short_description = 'Titer'

    def titration_unit(self, obj):
        try:
            return obj.titration_unit
        except:
            return None

    titration_unit.short_description = 'Unit'

    def titration_cell_type(self, obj):
        try:
            return obj.titration_cell_type
        except:
            return None

    titration_cell_type.short_description = 'Cell Type'

    def titration_code(self, obj):
        try:
            return obj.titration_code
        except:
            return None

    titration_code.short_description = 'Titration Code'

    def titration_date(self, obj):
        try:
            return obj.titration_date
        except:
            return None

    titration_date.short_description = 'Titration Date'

    def description(self, obj):
        try:
            return obj.description
        except:
            return None

    description.short_description = 'Description'


admin.site.register(CSampleVirusTitration, CSampleVirusTitrationAdmin)
