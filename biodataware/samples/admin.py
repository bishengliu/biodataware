from django.contrib import admin
from .models import Biosystem, Tissue, Sample, SampleAttachment, SampleTissue, SampleResearcher
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
    list_display = ['container', 'container_box', 'position',
                    'name', 'freezing_date', 'quantity', 'system', 'tissue', 'type', 'attachment', 'researcher',
                    'registration_code', 'pathology_code', 'freezing_code', 'code39', 'qrcode', 'description']

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

    def system(self, obj):
        try:
            return obj.sampleTissue.objects
        except:
            return None

    system.short_description = 'System'

    def tissue(self, obj):
        try:
            return obj.sampleTissue.objects
        except:
            return None

    tissue.short_description = 'tissue'

    def type(self, obj):
        try:
            return obj.sampleType.objects
        except:
            return None

    type.short_description = 'type'

    def attachment(self, obj):
        try:
            return obj.sampleAttachment.objects
        except:
            return None

    attachment.short_description = 'attachment'

    def researcher(self, obj):
        try:
            return obj.sampleResearcher.objects
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
