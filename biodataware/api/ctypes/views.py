from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from csamples.models import *
from .serializers import *
from groups.models import Group, GroupResearcher
from django.utils.safestring import mark_safe


class CTypeList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    # get all the shared and own group types
    def get(self, request, format=None):
        try:
            user = request.user
            obj = {'user': user}
            if user.is_superuser:
                ctypes = CType.objects.all()
                serializer = CTypeListSerializer(ctypes, many=True)
                return Response(serializer.data)
            else:
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                ctypes = CType.objects.all().filter(group_id__in=group_ids)
                serializer = CTypeListSerializer(ctypes, many=True)
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
                            description=data.get('description', '')
                        )
            return Response({'detail': 'material created!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, material type not created!'},
                            status=status.HTTP_400_BAD_REQUEST)


