from rest_framework import serializers
from csamples.models import *
from api.groups.serializers import GroupSerializer
from django.utils.translation import ugettext_lazy as _
import re



# =================== ctypes =================
class CTypeListSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    class Meta:
        model = CType
        fields = ('pk', 'type', 'group', 'is_public', 'description')


class CTypeCreateEditSerializer(serializers.Serializer):

    class Meta:
        model = CType
        fields = ('type', 'group_id', 'is_public', 'description')

    def validate_type(self, value):
        try:
            ctype_pattern = re.compile("^[a-zA-Z_-][a-zA-Z0-9_-]*$")
            if not ctype_pattern.search(value):
                msg = _("Material type name must only contain only letters, numbers (not at the beginning), \"-\" or \"_\"")
                raise serializers.ValidationError(msg)
            else:
                return value
        except:
            msg = _("Material type name validation failed!")
            raise serializers.ValidationError(msg)


