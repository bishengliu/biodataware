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
            if user.is_superuser:
                CTypeAttr.objects.create(**data)
                return Response({'detail': 'the attr added to the type!'}, status=status.HTTP_200_OK)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                if ctype.group_id not in group_ids:
                    return Response({'detail': 'Something went wrong, modification to the material type not allowed!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    CTypeAttr.objects.create(**data)
                    return Response({'detail': 'the attr added to the type!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, failed to add the attr to the material type!'},
                            status=status.HTTP_400_BAD_REQUEST)


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