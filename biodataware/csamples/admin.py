from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *


class CTypeAdmin(admin.ModelAdmin):
    list_display = ['type', 'group', 'public', 'description']

    def type(self, obj):
        try:
            return obj.type
        except:
            return None

    type.short_description = 'Type'

    def group(self, obj):
        try:
            return obj.group.group_name
        except:
            return None

    group.short_description = 'Group'

    def public(self, obj):
        try:
            return obj.public
        except:
            return None

    public.short_description = 'Public'

    def description(self, obj):
        try:
            return obj.description
        except:
            return None

    description.short_description = 'Description'


admin.site.register(CType, CTypeAdmin)


class CSampleAdmin(admin.ModelAdmin):
    list_display = ['name', 'container', 'container_box', 'ctype', 'position', 'storage_date',
                    'attachment', 'researcher', 'occupied', 'date_out', 'description']

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
    list_display = ['attr_name', 'attr_label', 'attr_value_type', 'attr_value_text_max_length',
                    'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required']

    def attr_name(self, obj):
        try:
            return obj.attr_name
        except:
            return None

    attr_name.short_description = 'Attr Name'

    def attr_label(self, obj):
        try:
            return obj.attr_label
        except:
            return None

        attr_label.short_description = 'Attr Label'

    def attr_value_type(self, obj):
        try:
            return obj.attr_value_type
        except:
            return None

    attr_value_type.short_description = 'Attr Value Type'

    def attr_value_text_max_length(self, obj):
        try:
            return obj.attr_value_text_max_length
        except:
            return None

    attr_value_text_max_length.short_description = 'Attr Text Value Max Length'

    def attr_value_decimal_total_digit(self, obj):
        try:
            return obj.attr_value_decimal_total_digit
        except:
            return None

    attr_value_decimal_total_digit.short_description = 'Attr Decimal Value Total Digit'

    def attr_value_decimal_point(self, obj):
        try:
            return obj.attr_value_decimal_point
        except:
            return None

    attr_value_decimal_point.short_description = 'Attr Decimal Points'

    def attr_required(self, obj):
        try:
            return obj.attr_required
        except:
            return None

    attr_required.short_description = 'Attr Required'

admin.site.register(CTypeMinimalAttr, CTypeMinimalAttrAdmin)


class CTypeAttrAdmin(admin.ModelAdmin):
    list_display = ['attr_name', 'attr_label', 'ctype', 'attr_value_type', 'attr_value_text_max_length',
                    'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required', 'attr_order', 'has_sub_attr']

    def ctype(self, obj):
        try:
            return obj.ctype.type
        except:
            return None

    ctype.short_description = 'Type'

    def attr_name(self, obj):
        try:
            return obj.attr_name
        except:
            return None

    attr_name.short_description = 'Attr Name'

    def attr_label(self, obj):
        try:
            return obj.attr_label
        except:
            return None

    attr_label.short_description = 'Attr Label'

    def attr_value_type(self, obj):
        try:
            return obj.attr_value_type
        except:
            return None

    attr_value_type.short_description = 'Attr Value Type'

    def attr_value_text_max_length(self, obj):
        try:
            return obj.attr_value_text_max_length
        except:
            return None

    attr_value_text_max_length.short_description = 'Attr Text Value Max Length'

    def attr_value_decimal_total_digit(self, obj):
        try:
            return obj.attr_value_decimal_total_digit
        except:
            return None

    attr_value_decimal_total_digit.short_description = 'Attr Decimal Value Total Digit'

    def attr_value_decimal_point(self, obj):
        try:
            return obj.attr_value_decimal_point
        except:
            return None

    attr_value_decimal_point.short_description = 'Attr Decimal Points'

    def attr_required(self, obj):
        try:
            return obj.attr_required
        except:
            return None

    attr_required.short_description = 'Attr Required'

    def attr_order(self, obj):
        try:
            return obj.attr_order
        except:
            return None

    attr_order.short_description = 'Attr Order'

    def has_sub_attr(self, obj):
        try:
            return obj.has_sub_attr
        except:
            return None

    has_sub_attr.short_description = 'Has SubAttr'

admin.site.register(CTypeAttr, CTypeAttrAdmin)


class CTypeSubAttrAdmin(admin.ModelAdmin):
    list_display = ['parent_attr', 'attr_name', 'attr_label', 'attr_value_type', 'attr_value_text_max_length',
                    'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required', 'attr_order']

    def parent_attr(self, obj):
        try:
            return obj.ctypeattr.attr_name
        except:
            return None

    parent_attr.short_description = 'Parent Attr'

    def attr_name(self, obj):
        try:
            return obj.attr_name
        except:
            return None

    attr_name.short_description = 'Attr Name'

    def attr_label(self, obj):
        try:
            return obj.attr_label
        except:
            return None

    attr_label.short_description = 'Attr Label'

    def attr_value_type(self, obj):
        try:
            return obj.attr_value_type
        except:
            return None

    attr_value_type.short_description = 'Attr Value Type'

    def attr_value_text_max_length(self, obj):
        try:
            return obj.attr_value_text_max_length
        except:
            return None

    attr_value_text_max_length.short_description = 'Attr Text Value Max Length'

    def attr_value_decimal_total_digit(self, obj):
        try:
            return obj.attr_value_decimal_total_digit
        except:
            return None

    attr_value_decimal_total_digit.short_description = 'Attr Decimal Value Total Digit'

    def attr_value_decimal_point(self, obj):
        try:
            return obj.attr_value_decimal_point
        except:
            return None

    attr_value_decimal_point.short_description = 'Attr Decimal Points'

    def attr_required(self, obj):
        try:
            return obj.attr_required
        except:
            return None

    attr_required.short_description = 'Attr Required'

    def attr_order(self, obj):
        try:
            return obj.attr_order
        except:
            return None

    attr_order.short_description = 'Attr Order'


admin.site.register(CTypeSubAttr, CTypeSubAttrAdmin)


class CSampleDataAdmin(admin.ModelAdmin):
    list_display = ['csample', 'container', 'container_box', 'ctype', 'ctype_attr', 'ctype_attr_value_part1', 'ctype_attr_value_part2']

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

    def csample(self, obj):
        try:
            return obj.csample.name
        except:
            return None

    csample.short_description = 'name'

    def ctype(self, obj):
        try:
            return obj.csample.ctype.type
        except:
            return None

    ctype.short_description = 'Type'

    def ctype_attr(self, obj):
        try:
            return obj.ctypeattr.attr_name
        except:
            return None

    ctype_attr.short_description = 'Attr'

    def ctype_attr_value_part1(self, obj):
        try:
            return obj.ctype_attr_value_part1
        except:
            return None

    ctype_attr_value_part1.short_description = 'Value_Part1'

    def ctype_attr_value_part2(self, obj):
        try:
            return obj.ctype_attr_value_part2
        except:
            return None

    ctype_attr_value_part2.short_description = 'Value_Part2'

admin.site.register(CSampleData, CSampleDataAdmin)


class CSampleSubDataAdmin(admin.ModelAdmin):
    list_display = ['csample', 'container', 'container_box', 'ctype', 'ctype_sub_attr', 'ctype_sub_attr_value_part1', 'ctype_sub_attr_value_part2']

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

    def csample(self, obj):
        try:
            return obj.csample.name
        except:
            return None

    csample.short_description = 'name'

    def ctype(self, obj):
        try:
            return obj.csample.ctype.type
        except:
            return None

    ctype.short_description = 'Type'

    def ctype_sub_attr(self, obj):
        try:
            return obj.ctypesubattr.attr_name
        except:
            return None

    ctype_sub_attr.short_description = 'SubAttr'

    def ctype_sub_attr_value_part1(self, obj):
        try:
            return obj.ctype_sub_attr_value_part1
        except:
            return None

    ctype_sub_attr_value_part1.short_description = 'Value_Part1'

    def ctype_sub_attr_value_part2(self, obj):
        try:
            return obj.ctype_sub_attr_value_part2
        except:
            return None

    ctype_sub_attr_value_part2.short_description = 'Value_Part2'


admin.site.register(CSampleSubData, CSampleSubDataAdmin)


class CSampleVirusTitrationAdmin(admin.ModelAdmin):
    list_display = ['csample', 'container', 'container_box', 'ctype', 'titration_titer', 'titration_unit', 'titration_cell_type',
                    'titration_code', 'titration_date', 'description']

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

    def ctype(self, obj):
        try:
            return obj.csample.ctype.type
        except:
            return None

    ctype.short_description = 'Type'

    def csample(self, obj):
        try:
            return obj.csample.name
        except:
            return None

    csample.short_description = 'Name'

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


class CSampleAttachmentAdmin(admin.ModelAdmin):
    list_display = ['csample', 'container', 'container_box', 'ctype', 'attachment', 'description']

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

    def ctype(self, obj):
        try:
            return obj.csample.ctype.type
        except:
            return None

    ctype.short_description = 'Type'

    def csample(self, obj):
        try:
            return obj.csample.name
        except:
            return None

    csample.short_description = 'Name'

    def attachment(self, obj):
        try:
            output = ''
            output += '<a href="' + obj.attachment.url + '" class="" alt="' + obj.label + '"><i></i><span>' + obj.label + '</span></a>' + '<br/>'
            return mark_safe(output)
        except:
            return None

    attachment.short_description = 'Attachment'

    def description(self, obj):
        try:
            return obj.description
        except:
            return None

    description.short_description = 'Description'

admin.site.register(CSampleAttachment, CSampleAttachmentAdmin)


class CSampleResearcherAdmin(admin.ModelAdmin):
    list_display = ['csample', 'container', 'container_box', 'ctype', 'researcher']

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

    def ctype(self, obj):
        try:
            return obj.csample.ctype.type
        except:
            return None

    ctype.short_description = 'Type'

    def csample(self, obj):
        try:
            return obj.csample.name
        except:
            return None

    csample.short_description = 'Name'

    def researcher(self, obj):
        try:
            return obj.researcher.username + ' (' + obj.researcher.email + ')'
        except:
            return None

    researcher.short_description = 'Researcher'

admin.site.register(CSampleResearcher, CSampleResearcherAdmin)