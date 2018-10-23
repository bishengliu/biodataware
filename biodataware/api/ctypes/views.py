from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from csamples.models import *
from .serializers import *
from groups.models import Group, GroupResearcher
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404


class CTypeList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    # get all the shared and own group types
    def get(self, request, format=None):
        try:
            user = request.user
            if user.is_superuser:
                ctypes = CType.objects.all()
                serializer = CTypeSerializer(ctypes, many=True)
                return Response(serializer.data)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                ctypes = CType.objects.all().filter(group_id__in=group_ids)
                serializer = CTypeSerializer(ctypes, many=True)
                return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong, failed to retrieve material types!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # new type
    def post(self, request, format=None):
        try:
            user = request.user
            serializer = CTypeCreateEditSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = request.data
            type_name = data.get('type').upper()
            if user.is_superuser:
                # create public types
                # check whether same type exists
                ctype = CType.objects.all().filter(type__iexact=type_name)
                if ctype:
                    return Response({'detail': 'Same type already exists, material type not created!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    CType.objects.create(
                        type=type_name,
                        group_id=None,
                        is_public=True,
                        description=mark_safe(data.get('description', ''))
                    )
            else:
                # create ctypes for own group
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                ctype_group_id = data.get('group_id', -1)
                if ctype_group_id not in group_ids:
                    return Response({'detail': 'Something went wrong, material type not created!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    # check whether same type exists
                    ctype = CType.objects.all().filter(type__iexact=type_name).filter(group_id=ctype_group_id)
                    if ctype:
                        return Response({'detail': 'Same type already exists, material type not created!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        CType.objects.create(
                            type=type_name,
                            group_id=ctype_group_id,
                            is_public=data.get('is_public'),
                            description=mark_safe(data.get('description', ''))
                        )
            return Response({'detail': 'the material type created!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, material type not created!'},
                            status=status.HTTP_400_BAD_REQUEST)


class CTypeValidation(APIView):

    def post(self, request, format=None):
        try:
            name = request.data.get('name', '')
            group_id = int(request.data.get('group_pk', -1))
            excluded_pk = int(request.data.get('excluded_pk', -1))
            ctype = CType()
            if group_id == -1:
                if excluded_pk > 0:
                    ctype = CType.objects.all()\
                        .filter(type__iexact=name).first()
                else:
                    ctype = CType.objects.all()\
                        .exclude(pk=excluded_pk)\
                        .filter(type__iexact=name).first()
            else:
                if excluded_pk > 0:
                    ctype = CType.objects.all()\
                        .exclude(pk=excluded_pk)\
                        .filter(type__iexact=name)\
                        .filter(group_id=group_id).first()
                else:
                    ctype = CType.objects.all()\
                        .filter(type__iexact=name)\
                        .filter(group_id=group_id).first()
            if ctype is not None:
                return Response({'matched': True})
            return Response({'matched': False})
        except:
            return Response({'matched': True})


class CTypeDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get a type detail
    def get(self, request, pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            serializer = CTypeSerializer(ctype)
            if ctype.is_public is True or user.is_superuser:
                return Response(serializer.data)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                if ctype.group_id in group_ids:
                    return Response(serializer.data)
                else:
                    return Response({'detail': 'The material type is not public!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to retrieve the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # update a type
    def put(self, request, pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            serializer = CTypeCreateEditSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = request.data
            type_name = data.get('type').upper()
            if user.is_superuser:
                existed_ctypes = CType.objects.all().exclude(pk=pk).filter(type__iexact=type_name)
                if existed_ctypes:
                    return Response({'detail': 'Something went wrong, material type not updated!'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                if ctype.group_id not in group_ids:
                    return Response({'detail': 'Something went wrong, material type not public!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    existed_ctypes = CType.objects.all().exclude(pk=pk).filter(type__iexact=type_name).filter(group_id=ctype.group_id)
                    if existed_ctypes:
                        return Response({'detail': 'Something went wrong, material type not updated!'},
                                        status=status.HTTP_400_BAD_REQUEST)
            ctype.type = type_name
            ctype.is_public = data.get('is_public')
            ctype.description = mark_safe(data.get('description', ''))
            ctype.save()
            return Response({'detail': 'the material type updated!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, failed to update the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # delete a type
    def delete(self, request, pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            csample = CSample.objects.all().filter(ctype_id=ctype.pk).first()
            if csample is not None:
                return Response({'detail': 'The material type is used, deletion not allowed!'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if user.is_superuser:
                    ctype.delete()
                else:
                    groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                    group_ids = [g.group_id for g in groupresearchers]
                    if ctype.group_id in group_ids:
                        ctype.delete()
                        return Response({'detail': 'the material type deleted!'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'detail': 'The material type was created by other group, deletion not allowed!'},
                                        status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to remove the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)


class CTypeAttrList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get the attr list
    def get(self, request, pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            serializer = CTypeSerializer(ctype)
            if ctype.is_public is True or user.is_superuser:
                return Response(serializer.data)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                if ctype.group_id in group_ids:
                    return Response(serializer.data)
                else:
                    return Response({'detail': 'The material type is not public!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to retrieve the attrs of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk, format=None):
        try:
            user = request.user
            serializer = CTypeAttrCreateEditSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = request.data
            ctype = get_object_or_404(CType, pk=pk)
            ctype_id = data.get('ctype_id')
            if ctype_id == ctype.pk:
                if user.is_superuser:
                    CTypeAttr.objects.create(**data)
                    return Response({'detail': 'the attr added to the type!'}, status=status.HTTP_200_OK)
                else:
                    groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                    group_ids = [g.group_id for g in groupresearchers]
                    if ctype.group_id not in group_ids:
                        return Response(
                            {'detail': 'Something went wrong, modification to the material type not allowed!'},
                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        CTypeAttr.objects.create(**data)
                        return Response({'detail': 'the attr added to the type!'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Something went wrong, failed to add the attr to the material type!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to add the attr to the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)


class CTypeAttrValidation(APIView):

    def post(self, request, pk, format=None):
        try:
            name = request.data.get('name', '')
            ctype_pk = int(request.data.get('ctype_pk', -1))
            excluded_pk = int(request.data.get('excluded_pk', -1))
            cattr = CTypeAttr()
            if excluded_pk > 0:
                cattr = CTypeAttr.objects.all() \
                    .filter(ctype_id=ctype_pk) \
                    .filter(attr_name__iexact=name).first()
            else:
                cattr = CTypeAttr.objects.all() \
                    .exclude(pk=excluded_pk) \
                    .filter(ctype_id=ctype_pk) \
                    .filter(attr_name__iexact=name).first()
            if cattr is not None:
                return Response({'matched': True})
            return Response({'matched': False})
        except:
            return Response({'matched': True})


class CTypeAttrDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # get an attr detail
    def get(self, request, pk, attr_pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            serializer = CTypeAttrSerializer(ctype_attr)
            if ctype.is_public is True or user.is_superuser:
                return Response(serializer.data)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                if ctype.group_id in group_ids:
                    return Response(serializer.data)
                else:
                    return Response({'detail': 'The material type is not public!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to retrieve the attr of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # put attr
    def put(self, request, pk, attr_pk, format=None):
        try:
            user = request.user
            serializer = CTypeAttrCreateEditSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = request.data
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            ctype_id = data.get('ctype_id')
            attr_id = data.get('pk')
            if int(ctype_id) == int(pk) and int(attr_id) == int(attr_pk):
                if user.is_superuser:
                    ctype_attr.attr_name = data.get('attr_name', None)
                    ctype_attr.attr_label = data.get('attr_label', None)
                    ctype_attr.attr_value_type = data.get('attr_value_type', None)
                    ctype_attr.attr_value_text_max_length = data.get('attr_value_text_max_length', None)
                    ctype_attr.attr_value_decimal_total_digit = data.get('attr_value_decimal_total_digit', None)
                    ctype_attr.attr_value_decimal_point = data.get('attr_value_decimal_point', None)
                    ctype_attr.attr_required = data.get('attr_required', False)
                    ctype_attr.attr_order = data.get('attr_order', 0)
                    ctype_attr.has_sub_attr = data.get('has_sub_attr', False)
                    ctype_attr.save()
                    return Response({'detail': 'the attr updated to the type!'}, status=status.HTTP_200_OK)
                else:
                    groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                    group_ids = [g.group_id for g in groupresearchers]
                    if ctype.group_id in group_ids:
                        ctype_attr.attr_name = data.get('attr_name', None)
                        ctype_attr.attr_label = data.get('attr_label', None)
                        ctype_attr.attr_value_type = data.get('attr_value_type', None)
                        ctype_attr.attr_value_text_max_length = data.get('attr_value_text_max_length', None)
                        ctype_attr.attr_value_decimal_total_digit = data.get('attr_value_decimal_total_digit', None)
                        ctype_attr.attr_value_decimal_point = data.get('attr_value_decimal_point', None)
                        ctype_attr.attr_required = data.get('attr_required', False)
                        ctype_attr.attr_order = data.get('attr_order', 0)
                        ctype_attr.has_sub_attr = data.get('has_sub_attr', False)
                        ctype_attr.save()
                        return Response({'detail': 'the attr updated to the type!'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'detail': 'The material type is not public!'},
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Something went wrong, failed to update the attr of the material type!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to update the attr of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # delete an attr
    def delete(self, request, pk, attr_pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            csample_data = CSampleData.objects.all() \
                .filter(csample__ctype_id=pk) \
                .filter(ctype_attr_id=attr_pk) \
                .first()
            if csample_data is not None:
                return Response({'detail': 'The attr is used, deletion not allowed!'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if user.is_superuser:
                    ctype_attr.delete()
                    return Response({'detail': 'the attr deleted!'}, status=status.HTTP_200_OK)
                else:
                    groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                    group_ids = [g.group_id for g in groupresearchers]
                    if ctype.group_id in group_ids:
                        ctype_attr.delete()
                        return Response({'detail': 'the attr deleted!'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'detail': 'The material type was created by other group, deletion not allowed!'},
                                        status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to remove the attr of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)


class CTypeSubAttrList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, attr_pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            serializer = CTypeAttrSerializer(ctype_attr)
            if ctype.is_public is True or user.is_superuser:
                return Response(serializer.data)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                if ctype.group_id in group_ids:
                    return Response(serializer.data)
                else:
                    return Response({'detail': 'The material type is not public!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to retrieve the attr of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk, attr_pk, format=None):
        try:
            user = request.user
            serializer = CtyepSubAttrCreateEditSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = request.data
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            if ctype_attr.pk == int(data.get('parent_attr_id')):
                if user.is_superuser:
                    CTypeSubAttr.objects.create(**data)
                    return Response({'detail': 'the subattr added to the type!'}, status=status.HTTP_200_OK)
                else:
                    groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                    group_ids = [g.group_id for g in groupresearchers]
                    if ctype.group_id not in group_ids:
                        return Response(
                            {'detail': 'Something went wrong, modification to the attr not allowed!'},
                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        CTypeSubAttr.objects.create(**data)
                        return Response({'detail': 'the subattr added to the type!'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Something went wrong, failed to add the sub attr to the main attr!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to add the sub attr to the main attr!'},
                            status=status.HTTP_400_BAD_REQUEST)


class CTypeSubAttrValidation(APIView):

    def post(self, request, pk, attr_pk, format=None):
        try:
            name = request.data.get('name', '')
            ctype_pk = int(request.data.get('ctype_pk', -1))
            attr_pk = int(request.data.get('attr_pk', -1))
            excluded_pk = int(request.data.get('excluded_pk', -1))
            subattr = CTypeSubAttr()
            if excluded_pk > 0:
                subattr = CTypeSubAttr.objects.all() \
                    .filter(parent_attr_id=ctype_pk) \
                    .filter(attr_name__iexact=name).first()
            else:
                subattr = CTypeSubAttr.objects.all() \
                    .exclude(pk=excluded_pk) \
                    .filter(parent_attr_id=attr_pk) \
                    .filter(attr_name__iexact=name).first()
            if subattr is not None:
                return Response({'matched': True})
            return Response({'matched': False})
        except:
            return Response({'matched': True})


class CTypeSubAttrDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, attr_pk, subattr_pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            ctype_subattr = get_object_or_404(CTypeSubAttr, pk=subattr_pk)
            serializer = CTypeSubAttrSerializer(ctype_subattr)
            if ctype.is_public is True or user.is_superuser:
                return Response(serializer.data)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                if ctype.group_id in group_ids:
                    return Response(serializer.data)
                else:
                    return Response({'detail': 'The material type is not public!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to retrieve the subattr of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, attr_pk, subattr_pk, format=None):
        try:
            user = request.user
            serializer = CtyepSubAttrCreateEditSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = request.data
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            ctype_subattr = get_object_or_404(CTypeSubAttr, pk=subattr_pk)
            if int(data.get('parent_attr_id')) == int(attr_pk) and int(data.get('pk')) == int(subattr_pk):
                if user.is_superuser:
                    ctype_subattr.attr_name = data.get('attr_name', None)
                    ctype_subattr.attr_label = data.get('attr_label', None)
                    ctype_subattr.attr_value_type = data.get('attr_value_type', None)
                    ctype_subattr.attr_value_text_max_length = data.get('attr_value_text_max_length', None)
                    ctype_subattr.attr_value_decimal_total_digit = data.get('attr_value_decimal_total_digit', None)
                    ctype_subattr.attr_value_decimal_point = data.get('attr_value_decimal_point', None)
                    ctype_subattr.attr_required = data.get('attr_required', False)
                    ctype_subattr.attr_order = data.get('attr_order', 0)
                    ctype_subattr.save()
                    return Response({'detail': 'the subattr updated to the type!'}, status=status.HTTP_200_OK)
                else:
                    groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                    group_ids = [g.group_id for g in groupresearchers]
                    if ctype.group_id in group_ids:
                        ctype_subattr.attr_name = data.get('attr_name', None)
                        ctype_subattr.attr_label = data.get('attr_label', None)
                        ctype_subattr.attr_value_type = data.get('attr_value_type', None)
                        ctype_subattr.attr_value_text_max_length = data.get('attr_value_text_max_length', None)
                        ctype_subattr.attr_value_decimal_total_digit = data.get('attr_value_decimal_total_digit', None)
                        ctype_subattr.attr_value_decimal_point = data.get('attr_value_decimal_point', None)
                        ctype_subattr.attr_required = data.get('attr_required', False)
                        ctype_subattr.attr_order = data.get('attr_order', 0)
                        ctype_subattr.save()
                        return Response({'detail': 'the subattr updated to the type!'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'detail': 'The material type is not public!'},
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Something went wrong, failed to update the subattr of the material type!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to update the subattr of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, attr_pk, subattr_pk, format=None):
        try:
            user = request.user
            ctype = get_object_or_404(CType, pk=pk)
            ctype_attr = get_object_or_404(CTypeAttr, pk=attr_pk)
            ctype_subattr = get_object_or_404(CTypeSubAttr, pk=subattr_pk)
            csample_subdata = CSampleSubData.objects.all() \
                .filter(csample__ctype_id=pk) \
                .filter(ctype_sub_attr_id=subattr_pk) \
                .first()
            if csample_subdata is not None:
                return Response({'detail': 'The subattr is used, deletion not allowed!'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if user.is_superuser:
                    ctype_subattr.delete()
                    return Response({'detail': 'the subattr deleted!'}, status=status.HTTP_200_OK)
                else:
                    groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                    group_ids = [g.group_id for g in groupresearchers]
                    if ctype.group_id in group_ids:
                        ctype_subattr.delete()
                        return Response({'detail': 'the subattr deleted!'}, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {'detail': 'The material type was created by other group, deletion not allowed!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to remove the subattr of the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)