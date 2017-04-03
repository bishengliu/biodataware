from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *
from helpers.acl import isManger, isInGroups

from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from api.permissions import IsManager, IsPIAssistantofUser


# all container list only for manager or admin
# for admin and manager get all the conatiners, otherwise only show current group containers
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

    def post(self, request, format=None):
        pass

# view, edit and delete container
class ContainerDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        container = get_object_or_404(Container, pk=pk)
        if user.is_superuser:
            serializer = ConatainerSerializer(container)
            return Response(serializer.data)
        else:
            # check which group has/have the container
            group_containers = GroupContainer.objects.all().filter(container_id=container.pk)
            if group_containers:
                group_container_ids = [gc.group_id for gc in group_containers]
                if len(group_container_ids) > 0:
                    if isInGroups(user, group_container_ids):
                        serializer = ConatainerSerializer(container)
                        return Response(serializer.data)

        return Response({'detail': 'permission denied!'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        container = get_object_or_404(Container, pk=pk)
        try:
            if user.is_superuser:
                serializer = ContainerCreateSerializer(container, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                serializer = ConatainerSerializer(container)
                return Response(serializer.data)
            else:
                # is manager
                if settings.ALLOW_PI_TO_MANAGE_CONTAINER:
                    if isManger(user):
                        pass
                    return Response({'detail': 'container info changed!'}, status=status.HTTP_200_OK)
                # is pi/assistant of the group
                if isPiorManager(user):
                    pass
                    return Response({'detail': 'container info changed!'}, status=status.HTTP_200_OK)

                return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        pass


# box list view
# manage box view