from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *
from helpers.acl import isManger

from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from api.permissions import IsManager, IsPIAssistantofUser


# all container list only for manager or admin
#
class ContainerList(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser, IsManager, IsPIAssistantofUser)

    def get(self, request, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        # filter the containers for the pi or assistant
        # show all the containers if pi or assistant is also the manager
        if isManger(user) or user.is_superuser:
            containers = Container.objects.all()
        else:
            # get the group id of the current user
            groupresearchers = GroupResearcher.object.all().filter(user_id=user.pk)
            group_ids = [g.group_id for g in groupresearchers]
            containers = Container.objects.all().fillter(groupcontainer_set__group_id__in=group_ids)

        serializer = ConatainerSerializer(containers, many=True)
        return Response(serializer.data)
