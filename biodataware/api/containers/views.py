from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *
from helpers.acl import isManger, isInGroups, isPIorAssistantofGroup
from django.db import transaction
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from api.permissions import IsManager, IsPIAssistantofUser, IsPI


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

    @transaction.atomic
    def post(self, request, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        try:
            if isManger(user) or user.is_superuser:
                serializer = ContainerCreateSerializer(data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                data = serializer.data
                container = Container(**data)
                container.save()
                return Response({'detail': 'container added!'}, status=status.HTTP_200_OK)
            else:
                # get the group id of the current user
                groupresearchers = GroupResearcher.object.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                serializer = ContainerCreateSerializer(data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                data = serializer.data
                container = Container(**data)
                container.save()
                # add container to groups
                for group_id in group_ids:
                    GroupContainer.objects.create(
                        container_id=container.pk,
                        group_id=group_id
                    )
                return Response({'detail': 'container added!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, container not added!'},
                            status=status.HTTP_400_BAD_REQUEST)


# view, edit and delete container
class ContainerDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        container = get_object_or_404(Container, pk=pk)
        if user.is_superuser or isManger(user):
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
            if user.is_superuser or isManger(user):
                serializer = ContainerUpdateSerializer(container, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'detail': 'container info changed!'}, status=status.HTTP_200_OK)
                #return Response(ConatainerSerializer(container).data)
            else:
                if settings.ALLOW_PI_TO_MANAGE_CONTAINER:
                    # check which group has/have the container
                    group_containers = GroupContainer.objects.all().filter(container_id=container.pk)
                    if group_containers:
                        group_container_ids = [gc.group_id for gc in group_containers]
                        # is pi/assistant of the group
                        if isPIorAssistantofGroup(user, group_container_ids):
                            # save data
                            serializer = ContainerUpdateSerializer(container, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response({'detail': 'container info changed!'}, status=status.HTTP_200_OK)
                return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        container = get_object_or_404(Container, pk=pk)
        try:
            if user.is_superuser or isManger(user):
                if container.groupcontainer_set:
                    return Response(
                        {'detail': 'container not deleted! The container is assigned to researcher group(s).'},
                        status=status.HTTP_400_BAD_REQUEST)
                if container.boxcontainer_set:
                    return Response({'detail': 'container not deleted! The container contains box(es).'},
                                    status=status.HTTP_400_BAD_REQUEST)
                container.delete()
                return Response({'detail': 'container deleted!'}, status=status.HTTP_200_OK)
            else:
                if settings.ALLOW_PI_TO_MANAGE_CONTAINER:
                    # check which group has/have the container
                    group_containers = GroupContainer.objects.all().filter(container_id=container.pk)
                    if group_containers:
                        # which groups the container is assigned to:
                        group_container_ids = [gc.group_id for gc in group_containers]
                        # is pi/assistant of the group
                        if isPIorAssistantofGroup(user, group_container_ids):
                            if container.groupcontainer_set:
                                return Response(
                                    {'detail': 'container not deleted! '
                                               '\The container is assigned to researcher group(s).'},
                                    status=status.HTTP_400_BAD_REQUEST)
                            if container.boxcontainer_set:
                                return Response({'detail': 'container not deleted! The container contains box(es).'},
                                                status=status.HTTP_400_BAD_REQUEST)
                            container.delete()
                            return Response({'detail': 'container deleted!'}, status=status.HTTP_200_OK)
                return Response({'detail': 'permission denied, container not deleted!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, container not deleted!'}, status=status.HTTP_400_BAD_REQUEST)


# group containers list
class GroupContainerList(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser, IsManager, IsPI)

    def get(self, request, ct_id, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        if isManger(user) or user.is_superuser:
            group_containers = GroupContainer.objects.all()
        else:
            # get the group id of the current user
            groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
            group_ids = [g.group_id for g in groupresearchers]
            group_containers = GroupContainer.objects.all().filter(group_id__in=group_ids)
        serializer = GroupContainerSerializer(group_containers, many=True)
        return Response(serializer.data)

    def post(self, request, ct_id, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        try:
            serializer = GroupContainerCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            group_container = GroupContainer(**data)
            group_container.save()
            return Response({'detail': 'Container is assigned to the group!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, container not assigned to the group!'},
                            status=status.HTTP_400_BAD_REQUEST)


# remove container from group
class GroupContainerDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser, IsManager, IsPI, )

    def get(self, request, ct_id,  pk, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        group_container = get_object_or_404(GroupContainer, pk= pk)
        serializer = GroupContainerSerializer(group_container)
        return Response(serializer.data)

    def delete(self, request, ct_id, pk, format=None):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        group_container = get_object_or_404(GroupContainer, pk=pk)
        try:
            # get the container
            container = get_object_or_404(Container, pk=group_container.group_id)
            if container.boxcontainer_set:
                return Response({'detail': 'the container was not removed from the group! '
                                           'The container contains box(es) of the group.'},
                                status=status.HTTP_400_BAD_REQUEST)
            group_container.delete()
        except:
            return Response({'detail': 'Something went wrong, the container was not removed from the group!'},
                            status=status.HTTP_400_BAD_REQUEST)



