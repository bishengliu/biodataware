from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status

from .serializers import *

from groups.models import Group, GroupResearcher


# group list
class GroupList(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            serializer = GroupDetailCreateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            group = Group(**data)
            group.save()
            return Response(serializer.data)
        except:
            return Response({'detail': 'group not added!'}, status=status.HTTP_400_BAD_REQUEST)


class GroupDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, pk, format=None):
        group = get_object_or_404(Group, pk=pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        group = get_object_or_404(Group, pk=pk)
        group.delete()
        return Response({'detail': 'group deleted!'})

    def put(self, request, pk, format=None):
        group = get_object_or_404(Group, pk=pk)
        serializer = GroupDetailCreateSerializer(group, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
