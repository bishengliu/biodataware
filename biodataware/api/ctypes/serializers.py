from rest_framework import serializers
from csamples.models import *
from api.groups.serializers import GroupSerializer
from django.utils.translation import ugettext_lazy as _
import re


# =================== ctypes =================
# class CTypeMinimalAttrList(serializers.ModelSerializer):
#
#     class Meta:
#         model = CTypeMinimalAttr
#         fields = ('attr_name', 'attr_label', 'attr_value_type', 'attr_value_text_max_length',
#                   'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required')


class CTypeSubAttrSerializer(serializers.ModelSerializer):
    parent_attr = serializers.StringRelatedField()

    class Meta:
        model = CTypeSubAttr
        fields = ('pk', 'parent_attr_id', 'parent_attr', 'attr_name', 'attr_label', 'attr_value_type', 'attr_value_text_max_length',
                  'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required', 'attr_order')


class CTypeAttrSerializer(serializers.ModelSerializer):
    subattrs = CTypeSubAttrSerializer(source='ctypesubattr_set', many=True)

    class Meta:
        model = CTypeAttr
        fields = ('pk', 'ctype_id', 'attr_name', 'attr_label', 'attr_value_type', 'attr_value_text_max_length',
                  'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required', 'attr_order',
                  'has_sub_attr', 'subattrs')


class CTypeSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    attrs = CTypeAttrSerializer(source='ctypeattr_set', many=True)

    class Meta:
        model = CType
        fields = ('pk', 'type', 'group', 'is_public', 'description', 'attrs')


class CTypeCreateEditSerializer(serializers.ModelSerializer):

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


class CTypeAttrCreateEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = CTypeAttr
        fields = ('pk', 'ctype_id', 'attr_name', 'attr_label', 'attr_value_type', 'attr_value_text_max_length',
                  'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required', 'attr_order',
                  'has_sub_attr')

    def validate_attr_name(self, value):
        try:
            attr_name_pattern = re.compile("^[a-zA-Z_-][a-zA-Z0-9_-]*$")
            if not attr_name_pattern.search(value):
                msg = _("Attr name must only contain only letters, numbers (not at the beginning), \"-\" or \"_\"")
                raise serializers.ValidationError(msg)
            else:
                return value
        except:
            msg = _("Attr name validation failed!")
            raise serializers.ValidationError(msg)

    def validate_attr_label(self, value):
        try:
            attr_label_pattern = re.compile("^[a-zA-Z_-][a-zA-Z0-9_-]*$")
            if not attr_label_pattern.search(value):
                msg = _("Attr label must only contain only letters, numbers (not at the beginning), \"-\" or \"_\"")
                raise serializers.ValidationError(msg)
            else:
                return value
        except:
            msg = _("Attr label validation failed!")
            raise serializers.ValidationError(msg)

    # def validate(self, data):
    #     if 'ctype_id' in data and 'attr_name' in data:
    #         ctype_attr = CTypeAttr.objects.all()\
    #             .filter(ctype_id=data['ctype_id'])\
    #             .filter(attr_name=data['attr_name'])
    #         if ctype_attr:
    #             msg = _("attr already in the type!")
    #             raise serializers.ValidationError(msg)
    #     return data


class CtyepSubAttrCreateEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = CTypeSubAttr
        fields = ('pk', 'parent_attr_id', 'attr_name', 'attr_label', 'attr_value_type', 'attr_value_text_max_length',
                  'attr_value_decimal_total_digit', 'attr_value_decimal_point', 'attr_required', 'attr_order')

    def validate_attr_name(self, value):
        try:
            attr_name_pattern = re.compile("^[a-zA-Z_-][a-zA-Z0-9_-]*$")
            if not attr_name_pattern.search(value):
                msg = _("Attr name must only contain only letters, numbers (not at the beginning), \"-\" or \"_\"")
                raise serializers.ValidationError(msg)
            else:
                return value
        except:
            msg = _("Attr name validation failed!")
            raise serializers.ValidationError(msg)

    def validate_attr_label(self, value):
        try:
            attr_label_pattern = re.compile("^[a-zA-Z_-][a-zA-Z0-9_-]*$")
            if not attr_label_pattern.search(value):
                msg = _("Attr label must only contain only letters, numbers (not at the beginning), \"-\" or \"_\"")
                raise serializers.ValidationError(msg)
            else:
                return value
        except:
            msg = _("Attr label validation failed!")
            raise serializers.ValidationError(msg)