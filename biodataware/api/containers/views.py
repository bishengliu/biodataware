from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *

from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group
from api.permissions import IsManager


# all container list only for manager or admin
class ContainerList(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser, IsManager,)

    def get(self, request, format=None):
        containers = Container.objects.all()
        serializer = ConatainerSerializer(containers, many=True)
        return Response(serializer.data)
