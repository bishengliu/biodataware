from django.contrib import admin
from .models import Biosystem, Tissue, Sample, SampleAttachment, SampleTissue, SampleResearcher, SampleTag, SampleDropdown
from django.utils.safestring import mark_safe


# register biosystem
class BiosystemAdmin(admin.ModelAdmin):
    list_display = ['system', 'description']

admin.site.register(Biosystem, BiosystemAdmin)


# register Tissue
class TissueAdmin(admin.ModelAdmin):
    list_display = ['tissue', 'description']

admin.site.register(Tissue, TissueAdmin)


# register Sample
class SampleAdmin(admin.ModelAdmin):
    list_display = ['sample', 'container', 'container_box', 'position', 'occupied', 'date_out',
                    'freezing_date', 'quantity', 'tissue', 'type', 'attachment', 'researcher',
                    'registration_code', 'pathology_code', 'freezing_code', 'code39', 'qrcode', 'description',
                    'label', 'tag', 'official_name', 'quantity_unit', 'reference_code', 'oligo_name', 's_or_as',
                    'oligo_sequence', 'oligo_length', 'oligo_GC', 'target_sequence', 'clone_number', 'against_260_280',
                    'feature', 'r_e_analysis', 'backbone', 'insert', 'first_max', 'marker', 'has_glycerol_stock', 'strain',
                    'passage_number', 'cell_amount', 'project', 'creator', 'plasmid', 'titration_titer', 'titration_unit',
                    'titration_cell_type', 'titration_code', 'tissue']

    def sample(self, obj):
        try:
            return obj.name
        except:
            return None
    sample.short_description = 'Sample'

    def container(self, obj):
        try:
            return obj.box.container.name
        except:
            return None

    container.short_description = 'Container'

    def container_box(self, obj):
        try:
            return str(obj.box.tower) + '-' + str(obj.box.shelf) + '-' + str(obj.box.box)
        except:
            return None

    container_box.short_description = 'Box'

    def position(self, obj):
        try:
            return obj.vposition + obj.hposition
        except:
            return None

    position.short_description = 'Position'

    def tissue(self, obj):
        try:
            tissues = obj.sampletissue_set.all()
            output = ''
            for t in tissues:
                output += t.tissue.tissue + ' (' + t.system.system + ')' + '<br/>'
            return mark_safe(output)
        except:
            return None

    tissue.short_description = 'tissue'

    def attachment(self, obj):
        try:
            attachments = obj.sampleattachment_set.all()
            output = ''
            for a in attachments:
                output += '<a href="' + a.attachment.url + '" class="" alt="' + a.label + '"><i></i><span>' + a.label + '</span></a>' + '<br/>'
            return mark_safe(output)
        except:
            return None

    attachment.short_description = 'attachment'

    def researcher(self, obj):
        try:
            researchers = obj.sampleresearcher_set.all()
            output = ''
            for r in researchers:
                output += r.researcher.username + ' (' + r.researcher.email + ')' + '<br/>'
            return mark_safe(output)
        except:
            return None

    researcher.short_description = 'researcher'


admin.site.register(Sample, SampleAdmin)


# register SampleAttachment
class SampleAttachmentAdmin(admin.ModelAdmin):
    list_display = ['container_box', 'sample', 'label', 'attachment', 'description']

    def container_box(self, obj):
        try:
            return obj.sample.box
        except:
            return None

    container_box.short_description = 'Box'

    def sample(self, obj):
        try:
            return obj.sample.name
        except:
            return None

        sample.short_description = 'Sample'

    def label(self, obj):
        try:
            return obj.label
        except:
            return None

    label.short_description = 'Label'

    def attachment(self, obj):
        try:
            return mark_safe('<a href=" ' + obj.attachment.url + ' class="" alt="' + obj.label + '"><i></i><span>' + obj.label + '</span></a>')
        except:
            return None

    attachment.short_description = 'Attachment'

    def description(self, obj):
        try:
            return obj.description
        except:
            return None

    description.short_description = 'Description'

admin.site.register(SampleAttachment, SampleAttachmentAdmin)


# register SampleTissue
class SampleTissueAdmin(admin.ModelAdmin):
    list_display = ['container_box', 'sample', 'system', 'tissue']

    def container_box(self, obj):
        try:
            return obj.sample.box
        except:
            return None

    container_box.short_description = 'Box'

    def sample(self, obj):
        try:
            return obj.sample.name
        except:
            return None

    sample.short_description = 'Sample'

    def system(self, obj):
        try:
            return obj.system.system
        except:
            return None

    system.short_description = 'System'

    def tissue(self, obj):
        try:
            return obj.tissue.tissue
        except:
            return None

    tissue.short_description = 'tissue'

admin.site.register(SampleTissue, SampleTissueAdmin)


# register SampleResearcher
class SampleResearcherAdmin(admin.ModelAdmin):
    list_display = ['container_box', 'sample', 'researcher']

    def container_box(self, obj):
        try:
            return obj.sample.box
        except:
            return None

    container_box.short_description = 'Box'

    def sample(self, obj):
        try:
            return obj.sample.name
        except:
            return None

    sample.short_description = 'Sample'

    def researcher(self, obj):
        try:
            return obj.researcher.username + ' (' + obj.researcher.email + ')'
        except:
            return None

    researcher.short_description = 'Researcher'

admin.site.register(SampleResearcher, SampleResearcherAdmin)


# sample tag
class SampleTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']

admin.site.register(SampleTag, SampleTagAdmin)


# sample drop down
class SampleDropdownAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']

admin.site.register(SampleDropdown, SampleDropdownAdmin)
