from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from .serializers import *
from helpers.acl import isInGroups, isPIorAssistantofGroup
from django.db import transaction
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from users.models import User
from samples.models import Biosystem, Tissue
from api.permissions import IsInGroupContanier, IsPIorReadOnly, IsPIorAssistantorOwner
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import re
import datetime
import json
from django.db.models import Q


# all container list only for manager or admin
# for admin and manager get all the conatiners, otherwise only show current group containers
class ContainerList(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly, )

    def get(self, request, format=None):
        try:
            user = request.user
            obj = {'user': user}
            if not user.is_superuser:
                self.check_object_permissions(request, obj)  # check the permission
            # filter the containers for the pi or assistant
            # show all the containers if pi or assistant is also the manager
            if user.is_superuser:
                containers = Container.objects.all()
                serializer = ConatainerSerializer(containers, many=True)
                return Response(serializer.data)
            else:
                # get the group id of the current user
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                containers = Container.objects.all().filter(groupcontainer__group_id__in=group_ids)
                serializer = ConatainerSerializer(containers, many=True)
                return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, format=None):
        try:
            user = request.user
            obj = {'user': user}
            if not user.is_superuser:
                self.check_object_permissions(request, obj)  # check the permission
            # parse data
            form_data = dict(request.data)

            # check upload photo
            has_photo = False
            if 'file' in form_data.keys():
                has_photo = True
            # form model data
            model = form_data['obj'][0]
            # load into dict
            obj = json.loads(model)

            serializer = ContainerCreateSerializer(data=obj, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            container = Container()
            if user.is_superuser:
                container.name = data.get('name')
                container.temperature = data.get('temperature', '')
                container.tower = data.get('tower')
                container.shelf = data.get('shelf')
                container.box = data.get('box')
                container.description = data.get('description', '')
                container.room = data.get('room', '')
                if has_photo:
                    container.photo = form_data['file'][0]
                container.save()
                return Response({'detail': 'container added!'}, status=status.HTTP_200_OK)
            else:
                # get the group id of the current user
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                try:
                    container.name = data.get('name')
                    container.temperature = data.get('temperature', '')
                    container.tower = data.get('tower')
                    container.shelf = data.get('shelf')
                    container.box = data.get('box')
                    container.description = data.get('description', '')
                    container.room = data.get('room', '')
                    if has_photo:
                        container.photo = form_data['file'][0]
                    container.save()
                    # add container to groups
                    for group_id in group_ids:
                        GroupContainer.objects.create(
                            container_id=container.pk,
                            group_id=group_id
                        )
                    return Response({'detail': 'container added!'}, status=status.HTTP_200_OK)
                except:
                    if has_photo and container.photo:
                        container.photo.delete()
                    return Response({'detail': 'Something went wrong, container not added!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, container not added!'},
                            status=status.HTTP_400_BAD_REQUEST)


class ContainerCount(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        container_count = Container.objects.all().count()
        return Response({'count': container_count}, status=status.HTTP_200_OK)


# search container info
# {'query': 'container_name', 'value': value, 'container_pk': -1 }
class ContainerSearch(APIView):

    def post(self, request, format=None):
        key = request.data.get('query', '')
        value = request.data.get('value', '')
        group_id = int(request.data.get('container_pk', -1))
        try:
            containers = Container.objects.all()
            if group_id >= 0:
                containers = containers.exclude(pk=group_id)
            if key == 'name' and value:
                container = containers.filter(name__iexact=value).first()
                if container:
                    return Response({'matched': True, 'container': ConatainerSerializer(container).data})
            return Response({'matched': False, 'group': ''})
        except:
            return Response({'detail': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


# view, edit and delete container
class ContainerDetail(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly, IsInGroupContanier, )

    def get(self, request, pk, format=None):
        user = request.user
        container = get_object_or_404(Container, pk=pk)
        obj = {'user': user, 'container': container}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
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
        container = get_object_or_404(Container, pk=pk)
        try:
            obj = {'user': user, 'container': container}
            if not user.is_superuser:
                self.check_object_permissions(request, obj)  # check the permission
            # parse data
            form_data = dict(request.data)
            # check upload photo
            has_photo = False
            if 'file' in form_data.keys():
                has_photo = True
            # form model data
            model = form_data['obj'][0]
            # load into dict
            obj = json.loads(model)

            serializer = ContainerUpdateSerializer(data=obj, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            # save the container
            container.name = data.get("name", "")
            container.room = data.get("room", "")
            container.temperature = data.get("temperature", "")
            container.tower = data.get("tower", 1)
            container.shelf = data.get("shelf", 1)
            container.box = data.get("box", 1)
            container.description = data.get("description", "")
            if has_photo:
                if container.photo:
                    container.photo.delete()
                container.photo = form_data['file'][0]
            if user.is_superuser:
                container.save()
                return Response({'detail': True}, status=status.HTTP_200_OK)
            else:
                # check which group has/have the container
                group_containers = GroupContainer.objects.all().filter(container_id=container.pk)
                if group_containers:
                    group_container_ids = [gc.group_id for gc in group_containers]
                    # is pi/assistant of the group
                    if isPIorAssistantofGroup(user, group_container_ids):
                        container.save()
                        return Response({'detail': True}, status=status.HTTP_200_OK)
                return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = request.user
        container = get_object_or_404(Container, pk=pk)
        try:
            obj = {'user': user, 'container': container}
            if not user.is_superuser:
                self.check_object_permissions(request, obj)  # check the permission
            if user.is_superuser:
                if container.groupcontainer_set.exists():
                    return Response(
                        {'detail': 'container not deleted! The container is assigned to researcher group(s).'},
                        status=status.HTTP_400_BAD_REQUEST)
                if container.boxcontainer_set.exists():
                    return Response({'detail': 'container not deleted! The container contains box(es).'},
                                    status=status.HTTP_400_BAD_REQUEST)
                container.delete()
                return Response({'detail': 'container deleted!'}, status=status.HTTP_200_OK)
            else:
                # check which group has/have the container
                group_containers = GroupContainer.objects.all().filter(container_id=container.pk)
                if group_containers:
                    # which groups the container is assigned to:
                    group_container_ids = [gc.group_id for gc in group_containers]
                    # is pi/assistant of the group
                    if isPIorAssistantofGroup(user, group_container_ids):
                        if container.groupcontainer_set.exclude(group_id__in=group_container_ids).exists():
                            return Response(
                                {'detail': 'container not deleted! '
                                           '\The container is assigned to researcher group(s).'},
                                status=status.HTTP_400_BAD_REQUEST)
                        if container.boxcontainer_set.exists():
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
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly, )

    def get(self, request, ct_id, format=None):
        user = request.user
        obj = {'user': user}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        try:
            if user.is_superuser:
                group_containers = GroupContainer.objects.all()
            else:
                # get the group id of the current user
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                group_containers = GroupContainer.objects.all().filter(group_id__in=group_ids)
            serializer = GroupContainerSerializer(group_containers, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, ct_id, format=None):
        user = request.user
        obj = {'user': user}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
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
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly, )

    def get(self, request, ct_id,  gp_id, format=None):
        user = request.user
        obj = {'user': user}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        try:
            group_containers = GroupContainer.objects.all().filter(container_id=ct_id).filter(group_id=gp_id)
            if group_containers:
                serializer = GroupContainerSerializer(group_containers.first())
                return Response(serializer.data)
            return Response({'detail': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, ct_id,  gp_id, format=None):
        user = request.user
        obj = {'user': user}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        try:
            group_containers = GroupContainer.objects.all().filter(container_id=ct_id).filter(group_id=gp_id)
            if group_containers:
                # get the container
                boxresearchers = BoxContainer.objects.all() \
                    .filter(container_id=ct_id) \
                    .filter(boxresearcher__researcher__group_id=gp_id)
                if boxresearchers:
                    return Response({'detail': False}, status=status.HTTP_200_OK)
                return Response({'detail': True}, status=status.HTTP_200_OK)
            return Response({'detail': False}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ct_id, gp_id, format=None):
        user = request.user
        obj = {'user': user}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        try:
            group_containers = GroupContainer.objects.all().filter(container_id=ct_id).filter(group_id=gp_id)
            if group_containers:
                boxresearchers = BoxContainer.objects.all() \
                    .filter(container_id=ct_id) \
                    .filter(boxresearcher__researcher__group_id=gp_id)
                if boxresearchers:
                    return Response({'detail': 'the container was not removed from the group! '
                                               'The container contains box(es) of the group.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                group_containers.first().delete()
                return Response({'detail': 'Container was removed from the group.'}, status=status.HTTP_200_OK)
            return Response({'detail': 'Something went wrong, the container was not removed from the group!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, the container was not removed from the group!'},
                            status=status.HTTP_400_BAD_REQUEST)


# return the current tower, with #of shelves
class Tower(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, ct_id, id, format=None):
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
        if int(id) > int(container.tower) or int(id) < 0:
            return Response({'detail': 'tower does not exist!'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = TowerSerializer({
            "container_pk": container.pk,
            "tower_id": int(id),
            "shelf_total": container.shelf
        })
        return Response(serializer.data)


# return the current shelf, with the list of boxes
class ShelfAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, )

    def get(self, request, ct_id, tw_id, sf_id, format=None):
        user = request.user
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
        obj = {'user': user, 'container': container}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        try:
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get the box of the shelf
            boxes = BoxContainer.objects.all().filter(container_id=int(ct_id)).filter(tower=int(tw_id)).filter(
                shelf=int(sf_id))
            serializer = BoxSamplesSerializer(boxes, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, ct_id, tw_id, sf_id, format=None):
        user = request.user
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
        obj = {'user': user, 'container': container}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        if int(tw_id) > int(container.tower) or int(tw_id) < 0:
            return Response({'detail': 'tower does not exist!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
            return Response({'detail': 'shelf does not exist!'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            # add box
            serializer = BoxContainerCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            # value the box
            if (int(data['box'])) < 0 or (int(data['box']) > container.box):
                return Response({'detail': 'Invalid box position!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # check the existence of the box
            bc = BoxContainer.objects.all() \
                .filter(container_id=container.pk) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=data['box'])
            if bc is None:
                return Response({'detail': 'box already exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box_container = BoxContainer.objects.create(
                container_id=int(ct_id),
                box_vertical=data['box_vertical'],
                box_horizontal=data['box_horizontal'],
                tower=int(tw_id),
                shelf=int(sf_id),
                box=data['box'],
                color=getattr(data, 'color', '#ffffff'),
                description=getattr(data, 'description', '')
            )
            box_researcher = BoxResearcher.objects.create(
                box_id=box_container.pk,
                researcher_id=user.pk
            )
            return Response({'detail': 'Box add!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Box not added!'},
                            status=status.HTTP_400_BAD_REQUEST)


# return the current shelf, with the list of boxes: 1-1-
class Shelf(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def get(self, request, ct_id, id, format=None):
        user = request.user
        container = get_object_or_404(Container, pk=int(ct_id))
        obj = {'user': user, 'container': container}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        # get the container
        # parse tw_id and sf_id
        id_list = id.split("-")
        tw_id = int(id_list[0])
        sf_id = int(id_list[1])
        if int(tw_id) > int(container.tower) or int(tw_id) < 0:
            return Response({'detail': 'tower does not exist!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
            return Response({'detail': 'shelf does not exist!'},
                            status=status.HTTP_400_BAD_REQUEST)
        # get the box of the shelf
        boxes = BoxContainer.objects.all().filter(container_id=int(ct_id)).filter(tower=int(tw_id)).filter(shelf=int(sf_id))
        serializer = BoxSamplesSerializer(boxes, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, ct_id, id, format=None):
        user = request.user
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
        obj = {'user': user, 'container': container}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        # parse tw_id and sf_id
        id_list = id.split("-")
        tw_id = int(id_list[0])
        sf_id = int(id_list[1])
        if int(tw_id) > int(container.tower) or int(tw_id) < 0:
            return Response({'detail': 'tower does not exist!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
            return Response({'detail': 'shelf does not exist!'},
                            status=status.HTTP_400_BAD_REQUEST)
        # add box
        try:
            serializer = BoxContainerCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            # validate the box
            if (int(data['box'])) < 0 or (int(data['box']) > container.box):
                return Response({'detail': 'Invalid box position!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # check the existence of the box
            bc = BoxContainer.objects.all() \
                .filter(container_id=container.pk) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=data['box'])
            if bc is None:
                return Response({'detail': 'box already exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box_container = BoxContainer.objects.create(
                container_id=int(ct_id),
                box_vertical=data['box_vertical'],
                box_horizontal=data['box_horizontal'],
                tower=int(tw_id),
                shelf=int(sf_id),
                box=data['box'],
                color=getattr(data, 'color', '#ffffff'),
                description=getattr(data, 'description', '')
            )
            box_researcher = BoxResearcher.objects.create(
                box_id=box_container.pk,
                researcher_id=user.pk
            )
            return Response({'detail': 'Box add!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Box not added!'},
                                status=status.HTTP_400_BAD_REQUEST)


# group boxes list of a container, quick access
class ContainerBoxList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def get(self, request, ct_id, format=None):
        user = request.user
        # get the container
        container = get_object_or_404(Container, pk=ct_id)
        try:
            # get the boxes
            if user.is_superuser:
                boxes = BoxContainer.objects.all().filter(container_id=container.pk)
                serializer = BoxSamplesSerializer(boxes, many=True)
                return Response(serializer.data)
            else:
                obj = {'user': user, 'container': container}
                if not user.is_superuser:
                    self.check_object_permissions(request, obj)  # check the permission

                # get only the researchers of the group(s)
                researcher_ids = []
                group_ids = []
                # get the current group id
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                if groupresearchers:
                    group_ids = [g.group_id for g in groupresearchers]
                # get all the researchers in the groups
                researchers = GroupResearcher.objects.all().filter(group_id__in=group_ids)
                if researchers:
                    researcher_ids = [r.user_id for r in researchers]
                    # get all the researchers in the group
                boxes = BoxContainer.objects.all().filter(container_id=container.pk) \
                        .filter(boxresearcher__researcher_id__in=researcher_ids)
                serializer = BoxSamplesSerializer(boxes, many=True)
                return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, ct_id, format=None):
        user = request.user
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
        obj = {'user': user, 'container': container}
        if not user.is_superuser:
            self.check_object_permissions(request, obj)  # check the permission
        # add box
        try:
            serializer = ContainerBoxCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            tw_id = int(data['tower'])
            sf_id = int(data['shelf'])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if (int(data['box'])) < 0 or (int(data['box']) > container.box):
                return Response({'detail': 'Invalid box position!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # check the existence of the box
            bc = BoxContainer.objects.all() \
                .filter(container_id=container.pk) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=data['box'])
            if bc is None:
                return Response({'detail': 'box already exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box_container = BoxContainer.objects.create(
                container_id=int(ct_id),
                box_vertical=data['box_vertical'],
                box_horizontal=data['box_horizontal'],
                tower=int(tw_id),
                shelf=int(sf_id),
                box=data['box'],
                color=getattr(data, 'color', '#ffffff'),
                description=getattr(data, 'description', '')
            )
            box_container.save()
            box_researcher = BoxResearcher.objects.create(
                box_id=box_container.pk,
                researcher_id=user.pk
            )
            box_researcher.save()
            return Response({'detail': 'Box add!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Box not added!'},
                            status=status.HTTP_400_BAD_REQUEST)


# get group favorite boxes
class ContainerFavoriteBoxList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def get(self, request, ct_id, format=None):
        user = request.user
        # get the container
        container = get_object_or_404(Container, pk=ct_id)
        try:
            # get the boxes
            if user.is_superuser:
                boxes = BoxContainer.objects.all().filter(container_id=container.pk).filter(rate__gte=1)
                serializer = BoxSamplesSerializer(boxes, many=True)
                return Response(serializer.data)
            else:
                obj = {'user': user, 'container': container}
                if not user.is_superuser:
                    self.check_object_permissions(request, obj)  # check the permission
                # get only the researchers of the group(s)
                researcher_ids = []
                group_ids = []
                # get the current group id
                groupresearchers = GroupResearcher.objects.all().filter(user_id=user.pk)
                if groupresearchers:
                    group_ids = [g.group_id for g in groupresearchers]
                # get all the researchers in the groups
                researchers = GroupResearcher.objects.all().filter(group_id__in=group_ids)
                if researchers:
                    researcher_ids = [r.user_id for r in researchers]
                boxes = BoxContainer.objects.all() \
                    .filter(container_id=container.pk) \
                    .filter(rate__gte=1) \
                    .filter(boxresearcher__researcher_id__in=researcher_ids)
                serializer = BoxSamplesSerializer(boxes, many=True)
                return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# get all the boxes in a container, including the boxes of othe groups
class ContainerAllBoxList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, ct_id, format=None):

        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            boxes = BoxContainer.objects.all().filter(container_id=container.pk)
            serializer = BoxSamplesSerializer(boxes, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

# ==============================================================
# allow view and add samples
# box and sample list
# =====================================


# need to apply permissions to only allow view the box details in the group
class BoxAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, )

    def get(self, request, ct_id, tw_id, sf_id, bx_id, format=None):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                serializer = BoxSamplesSerializer(box)
                return Response(serializer.data)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                    status=status.HTTP_400_BAD_REQUEST)

    # delete box
    def delete(self, request, ct_id, tw_id, sf_id, bx_id, format=None):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # check samples
                if box.sample_set:
                    return Response({'detail': 'Cannot delete this box, there are samples in the box!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                box.delete()
                return Response({'detail': 'Box deleted!'},
                                status=status.HTTP_200_OK)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                    status=status.HTTP_400_BAD_REQUEST)

    # add sample
    @transaction.atomic
    def post(self, request, ct_id, tw_id, sf_id, bx_id, format=None):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                serializer = SampleCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                data = serializer.data
                # check whether the position of the sample has already be occupied
                if Sample.objects.all().filter(box_id=box.pk).filter(hposition=data.get("hposition", "")).filter(vposition=data.get("vposition", "")).filter(occupied=True):
                    return Response({'detail': 'Sample position has already been taken!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # save sample
                sample = Sample.objects.create(
                    box_id=box.pk,
                    hposition=data['hposition'],
                    vposition=data['vposition'],
                    color=data.get('color', '#EEEEEE'),
                    name=data['name'],
                    occupied=True,
                    date_in=datetime.datetime.now(),
                    freezing_date=data.get('freezing_date', datetime.datetime.now()),
                    registration_code=data.get('registration_code', ''),
                    pathology_code=data.get('pathology_code', ''),
                    freezing_code=data.get('freezing_code', ''),
                    quantity=data['quantity'],
                    type=data.get('type', ''),
                    description=data.get('description', ''),
                    tissue=data.get('tissue', "")
                )

                # save sample attachments
                # separated by '|'
                if data.get('label', "") != "":
                    if "|" in data.get('label', "") and "|" in data.get("attachment_description", ""):
                        labels = data.get('label', "").split("|")
                        descriptions = data.get("attachment_description", "").split("|")
                        if len(labels) == len(descriptions):
                            for l in list(range(len(labels))):
                                SampleAttachment.objects.create(
                                    sample_id=sample.pk,
                                    label=labels[l],
                                    description=descriptions[l],
                                    # attachment name=attachment0, 1, 2...
                                    attachment=request.FILES['attachment' + str(l)] if (request.FILES and request.FILES['attachment' + str(l)]) else None
                                )
                    else:
                        SampleAttachment.objects.create(
                            sample_id=sample.pk,
                            label=data.get('label', ""),
                            description=data.get("attachment_description", ""),
                            attachment=request.FILES['attachment'] if (request.FILES and request.FILES['attachment']) else None
                        )

                # save sample researcher
                if data.get('researcher', "") != "":
                    if "," in data.get('researcher', ""):
                        researchers = data.get('researcher', "").split(",")
                        for r in list(range(len(researchers))):
                            # validate suer
                            if get_object_or_404(User, pk=int(researchers[r])):
                                SampleResearcher.objects.create(
                                    sample_id=sample.pk,
                                    researcher_id=int(researchers[r])
                                )
                    else:
                        if get_object_or_404(User, pk=int(data.get('researcher', ""))):
                            SampleResearcher.objects.create(
                                sample_id=sample.pk,
                                researcher_id=int(data.get('researcher', ""))
                            )
                return Response({'detail': 'sample saved!'},
                                status=status.HTTP_200_OK)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                    status=status.HTTP_400_BAD_REQUEST)


# box and sample list
class Box(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, )

    def get(self, request, ct_id, id, format=None):
        try:
            authUser = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if not authUser.is_superuser:
                if box_researcher is not None:
                    user = get_object_or_404(User, pk=box_researcher.researcher_id)
                    obj = {'user': user, 'container': container}
                    self.check_object_permissions(request, obj)  # check the permission
                    serializer = BoxSamplesSerializer(box)
                    return Response(serializer.data)
                return Response({'detail': 'Permission denied!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = BoxSamplesSerializer(box)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                    status=status.HTTP_400_BAD_REQUEST)

    # delete box
    def delete(self, request, ct_id, id, format=None):
        try:
            authUser = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if authUser.is_superuser or box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                if not authUser.is_superuser:
                    self.check_object_permissions(request, obj)  # check the permission
                # check samples
                if box.sample_set:
                    return Response({'detail': 'Cannot delete this box, there are samples in the box!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                box.delete()
                return Response({'detail': 'Box deleted!'},
                                status=status.HTTP_200_OK)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                    status=status.HTTP_400_BAD_REQUEST)

    # add sample
    @transaction.atomic
    def post(self, request, ct_id, id, format=None):
        try:
            user = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            if not user.is_superuser:
                self.check_object_permissions(request, {'user': user, 'container': container})  # check the permission
            # parse data
            form_data = dict(request.data)
            # slots
            slots = json.loads(form_data['slots'][0])
            # check upload photo
            has_attachment = False
            if 'file' in form_data.keys():
                has_attachment = True
                attachment_info = json.loads(form_data['attachment_info'][0])
                attachment_serializer = SampleAttachmentInfoSerializer(data=attachment_info, partial=True)
                attachment_serializer.is_valid(raise_exception=True)
                attachment_data = attachment_serializer.data
            # form model data and load into dict
            sample_obj = json.loads(form_data['obj'][0])

            serializer = SampleCreateSerializer(data=sample_obj, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            id_list = id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not user.is_superuser:
                # get box researcher
                box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
                if box_researcher is not None:
                    box_user = get_object_or_404(User, pk=box_researcher.researcher_id)
                    self.check_object_permissions(request, {'user': box_user})

            # loop slots
            # for return the pk of stored ids
            saved_slots = []
            for slot in slots:
                sampleAttachment = SampleAttachment()
                try:
                    match = re.match(r"([a-z]+)([0-9]+)", slot, re.I)
                    if match:
                        pos = match.groups()
                        sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                            hposition=pos[1]).filter(occupied=True).first()
                        if sample is None:
                            sample = Sample.objects.create(
                                box_id=box.pk,
                                hposition=pos[1],
                                vposition=pos[0],
                                color=data.get('color', '#EEEEEE'),
                                type=data.get('type', 'GENERAL'),
                                name=data.get('name'),
                                official_name=data.get('official_name', ''),
                                label=data.get('label', ''),
                                tag=data.get('tag', ''),
                                occupied=True,
                                date_in=datetime.datetime.now(),
                                freezing_date=data.get('freezing_date', datetime.datetime.now()),
                                registration_code=data.get('registration_code', ''),
                                freezing_code=data.get('freezing_code', ''),
                                quantity=data.get('quantity'),
                                quantity_unit=data.get('quantity_unit', ''),
                                reference_code=data.get('reference_code', ''),
                                description=data.get('description', ''),
                                # tissue
                                pathology_code=data.get('pathology_code', ''),
                                tissue=data.get('tissue', ""),

                                # (gRNA) Oligo only
                                oligo_name=data.get('oligo_name', ""),
                                s_or_as=data.get('s_or_as'),
                                oligo_sequence=data.get('oligo_sequence', ""),
                                oligo_length=data.get('oligo_length'),
                                oligo_GC=data.get('oligo_GC'),
                                target_sequence=data.get('target_sequence', ""),

                                # construct only
                                clone_number=data.get('clone_number', ""),
                                against_260_280=data.get('against_260_280'),
                                feature=data.get('feature', ""),
                                r_e_analysis=data.get('r_e_analysis', ""),
                                backbone=data.get('backbone', ""),
                                insert=data.get('insert', ""),
                                first_max=data.get('first_max', ""),
                                marker=data.get('marker', ""),
                                has_glycerol_stock=data.get('has_glycerol_stock'),
                                strain=data.get('strain', ""),
                                # cell line
                                passage_number=data.get('passage_number', ""),
                                cell_amount=data.get('cell_amount', ""),
                                project=data.get('project', ""),
                                creator=data.get('creator', ""),

                                # virus
                                plasmid=data.get('plasmid', ""),
                                titration_titer=data.get('titration_titer', ""),
                                titration_unit=data.get('titration_unit', ""),
                                titration_cell_type=data.get('titration_cell_type', ""),
                                titration_code=data.get('titration_code', "")
                            )

                            SampleResearcher.objects.create(
                                sample_id=sample.pk,
                                researcher_id=user.pk
                            )

                            # save sample attachments
                            if has_attachment:
                                sampleAttachment.sample_id = sample.pk
                                sampleAttachment.attachment = form_data['file'][0]
                                attachment_name = attachment_data.get('attachment_name')
                                sampleAttachment.label = attachment_data.get('label', attachment_name)
                                sampleAttachment.description = attachment_data.get('description', attachment_name)
                                sampleAttachment.save()

                            # append stored slots
                            saved_slots.append(slot)
                except:
                    if has_attachment and sampleAttachment.attachment:
                        sampleAttachment.attachment.delete()
            return Response({'slots': ','.join(saved_slots)},
                            status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# update box rate
class BoxRate(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def put(self, request, ct_id, id, format=None):
        try:
            auth_user = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = BoxRateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            box.rate = data['rate']
            if auth_user.is_superuser:
                box.save()
                return Response({'detail': 'rate is updated!'},
                            status=status.HTTP_200_OK)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is None:
                box.save()
                return Response({'detail': 'rate is updated!'},
                                status=status.HTTP_200_OK)
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                box.save()
                return Response({'detail': 'rate is updated!'},
                                status=status.HTTP_200_OK)

            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, box rate not updated!'},
                            status=status.HTTP_400_BAD_REQUEST)


# update box color
class BoxColor(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def put(self, request, ct_id, id, format=None):
        try:
            auth_user = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = BoxColorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            box.color = data['color']
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None and not auth_user.is_superuser:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
            box.save()
            return Response({'detail': 'color is updated!'},
                                status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, box color not updated!'},
                            status=status.HTTP_400_BAD_REQUEST)


# update box description
class BoxDescription(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def put(self, request, ct_id, id, format=None):
        try:
            auth_user = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = BoxDescriptionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            box.description = data['description']

            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if not auth_user.is_superuser:
                if box_researcher is not None:
                    user = get_object_or_404(User, pk=box_researcher.researcher_id)
                    obj = {'user': user, 'container': container}
                    self.check_object_permissions(request, obj)  # check the permission
            box.save()
            return Response({'detail': 'box description is updated!'},
                                status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, box description not updated!'},
                            status=status.HTTP_400_BAD_REQUEST)


# update box label
class BoxLabel(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def put(self, request, ct_id, id, format=None):
        try:
            auth_user = request.user
            serializer = BoxLabelSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box.label = data['label']
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if not auth_user.is_superuser:
                if box_researcher is not None:
                    user = get_object_or_404(User, pk=box_researcher.researcher_id)
                    obj = {'user': user, 'container': container}
                    self.check_object_permissions(request, obj)  # check the permission
            box.save()
            return Response({'detail': 'box label is updated!'},
                            status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, box label not updated!'},
                            status=status.HTTP_400_BAD_REQUEST)


# move container box
class MoveBox(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    #@transaction.atomic
    def post(self, request, format=None):
        try:
            auth_user = request.user
            serializer = MoveBoxSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            #ori_box_full_position
            ori_box_full_position = data.get('box_full_position', '')
            ori_box_match = re.match(r"^([0-9]+)-([0-9]+)-([0-9]+)$", ori_box_full_position, re.I)

            # target_box_full_position
            target_box_full_position = data.get('target_box_full_position', '')
            target_box_match = re.match(r"^([0-9]+)-([0-9]+)-([0-9]+)$", target_box_full_position, re.I)

            if(ori_box_match and target_box_match):
                ori_box_position_list = ori_box_full_position.split("-")
                ori_tw_id = int(ori_box_position_list[0])
                ori_sf_id = int(ori_box_position_list[1])
                ori_bx_id = int(ori_box_position_list[2])

                target_box_position_list = target_box_full_position.split("-")
                target_tw_id = int(target_box_position_list[0])
                target_sf_id = int(target_box_position_list[1])
                target_bx_id = int(target_box_position_list[2])

                # original container
                original_container_pk = data.get('original_container', -9999)
                original_container = get_object_or_404(Container, pk=int(original_container_pk))

                # target_container
                target_container_pk = data.get('target_container', -9999)
                target_container = get_object_or_404(Container, pk=int(target_container_pk))

                # ori box
                ori_box = BoxContainer.objects.all() \
                    .filter(container_id=int(original_container_pk)) \
                    .filter(tower=int(ori_tw_id)) \
                    .filter(shelf=int(ori_sf_id)) \
                    .filter(box=int(ori_bx_id)) \
                    .first()

                if ori_box is not None:
                    if not auth_user.is_superuser:
                        # get box researcher
                        ori_box_researcher = BoxResearcher.objects.all().filter(box_id=ori_box.pk).first()
                        if ori_box_researcher is not None:
                            ori_box_user = get_object_or_404(User, pk=ori_box_researcher.researcher_id)
                            obj = {'user': ori_box_user, 'container': original_container}
                            self.check_object_permissions(request, obj)  # check the permission
                    # check the target box
                    target_box = BoxContainer.objects.all() \
                        .filter(container_id=int(target_container_pk)) \
                        .filter(tower=int(target_tw_id)) \
                        .filter(shelf=int(target_sf_id)) \
                        .filter(box=int(target_bx_id)) \
                        .first()
                    if target_box is not None:
                        if not auth_user.is_superuser:
                            # get box researcher
                            target_box_researcher = BoxResearcher.objects.all().filter(box_id=target_box.pk).first()
                            if target_box_researcher is not None:
                                target_box_user = get_object_or_404(User, pk=target_box_researcher.researcher_id)
                                obj = {'user': target_box_user, 'container': target_container}
                                self.check_object_permissions(request, obj)  # check the permission
                        # check whether the boxes matches
                        if(ori_box.box_horizontal == target_box.box_horizontal and ori_box.box_vertical == target_box.box_vertical):
                            # target box is not empty and switch the boexes the box
                            ori_box.container = target_container
                            ori_box.tower = target_tw_id
                            ori_box.shelf = target_sf_id
                            ori_box.box = target_bx_id
                            ori_box.save()
                            target_box.container = original_container
                            target_box.tower = ori_tw_id
                            target_box.shelf = ori_sf_id
                            target_box.box = ori_bx_id
                            target_box.save()
                            return Response({'detail': 'box moved!'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'detail': 'box layouts do not match, box not moved!'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # target is empty and move the box
                        # find the first box record
                        target_container_first_box = BoxContainer.objects.all().filter(container_id=int(target_container_pk)).first()
                        if target_container_first_box is not None:
                            if (ori_box.box_horizontal != target_container_first_box.box_horizontal or ori_box.box_vertical != target_container_first_box.box_vertical):
                                return Response({'detail': 'box layouts do not match, box not moved!'},
                                                status=status.HTTP_400_BAD_REQUEST)
                        ori_box.container = target_container
                        ori_box.tower = target_tw_id
                        ori_box.shelf = target_sf_id
                        ori_box.box = target_bx_id
                        ori_box.save()
                        return Response({'detail': 'box moved!'}, status=status.HTTP_200_OK)
            return Response({'detail': 'Something went wrong, box not moved!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, box not moved!'},
                            status=status.HTTP_400_BAD_REQUEST)


# add a box to container
class AddBox(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    #@transaction.atomic
    def put(self, request, pk, format=None):
        try:
            user = request.user
            container = get_object_or_404(Container, pk=pk)
            obj = {'user': user, 'container': container}
            if not user.is_superuser:
                self.check_object_permissions(request, obj)  # check the permission
            serializer = AddBoxSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            # box position
            box_full_position = data.get('box_full_position', '')
            box_match = re.match(r"^([0-9]+)-([0-9]+)-([0-9]+)$", box_full_position, re.I)
            if box_match:
                # parse tower, shelf and box
                box_position_list = box_full_position.split("-")
                tw_id = int(box_position_list[0])
                sf_id = int(box_position_list[1])
                bx_id = int(box_position_list[2])
                box_found = BoxContainer.objects.all() \
                        .filter(container_id=int(container.pk)) \
                        .filter(tower=int(tw_id)) \
                        .filter(shelf=int(sf_id)) \
                        .filter(box=int(bx_id)) \
                        .first()
                if box_found is None:
                    box = BoxContainer.objects.create(
                        container=container,
                        tower=tw_id,
                        shelf=sf_id,
                        box=bx_id,
                        box_horizontal=data.get('box_horizontal', 1),
                        box_vertical=data.get('box_vertical', 1)
                    )
                    box.save()
                    # add box researcher
                    box_researcher = BoxResearcher.objects.create(
                        box_id=box.pk,
                        researcher_id=user.pk
                    )
                    box_researcher.save()
                    return Response({'detail': 'box added!'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Something went wrong, failed to add the box!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, failed to add the box!'},
                            status=status.HTTP_400_BAD_REQUEST)


# get, put and delete sample
class SampleDetailAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, )

    def get(self, request, ct_id, tw_id, sf_id, bx_id, sp_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        serializer = SampleSerializer(sample)
                        return Response(serializer.data)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, ct_id, tw_id, sf_id, bx_id, sp_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        sample.delete()
                        return Response({'detail': 'sample is removed!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# get, put and delete sample
class SampleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, )

    def get(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        serializer = SampleSerializer(sample)
                        return Response(serializer.data)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        sample.delete()
                        return Response({'detail': 'sample is removed!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# update single data attr
class SampleDetailUpdate(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                    status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        data = request.data
                        key = data.get('key', '')
                        value = data.get('value', '')
                        setattr(sample, key, value);
                        sample.save()
                        return Response({'detail': 'sample ' + key + ' saved!'},
                                        status=status.HTTP_200_OK)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# update single sample position
class UpdateSamplePosition(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    @transaction.atomic
    def put(self, request, ct_id, bx_id, sp_id):
        try:
            auth_user = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # find the sample
            match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
            data = request.data
            new_vposition = data.get('new_vposition', '')
            new_hposition = data.get('new_hposition', '')
            if match:
                pos = match.groups()
                sample_vposition = pos[0]
                sample_hposition = pos[1]
                sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=sample_vposition).filter(
                    hposition=sample_hposition).filter(occupied__iexact=1).first()
                switch_sample = Sample.objects.all().filter(box_id=box.pk).exclude(pk=sample.pk).filter(
                    vposition__iexact=new_vposition).filter(hposition=new_hposition).filter(occupied__iexact=1).first()
                if sample is None:
                    return Response({'detail': 'Something went wrong, sample not found!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                sample.vposition = new_vposition
                sample.hposition = new_hposition

                if not auth_user.is_superuser:
                    box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
                    if box_researcher is not None:
                        user = get_object_or_404(User, pk=box_researcher.researcher_id)
                        obj = {'user': user, 'container': container}
                        self.check_object_permissions(request, obj)  # check the permission

                if switch_sample is not None:
                    sample.save()
                    switch_sample.vposition = sample_vposition
                    switch_sample.hposition = sample_hposition
                    switch_sample.save()
                    return Response({'detail': 'sample position saved!'},
                                    status=status.HTTP_200_OK)
                else:
                    sample.save()
                    return Response({'detail': 'sample position saved!'},
                                    status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Something went wrong, sample not found!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# 2 samples, switch positions
class SampleSwitchPosition(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    @transaction.atomic
    def put(self, request, ct_id, bx_id):
        try:
            auth_user = request.user
            container = get_object_or_404(Container, pk=int(ct_id))
            # data
            serializer = SwitchSampleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            # the 2 samples
            first_sample = data.get('first_sample', '')
            second_sample = data.get('second_sample', '')
            first_match= re.match(r"([a-z]+)([0-9]+)", first_sample, re.I)
            second_match = re.match(r"([a-z]+)([0-9]+)", second_sample, re.I)
            # box position
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if first_match and second_match:
                first_pos = first_match.groups()
                # current sample
                sample1 = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=first_pos[0]).filter(
                    hposition=first_pos[1]).filter(occupied__iexact=1).first()
                second_pos = second_match.groups()
                # current sample
                sample2 = Sample.objects.all().filter(box_id=box.pk).filter(
                    vposition__iexact=second_pos[0]).filter(
                    hposition=second_pos[1]).filter(occupied__iexact=1).first()
                if sample1 is not None and sample2 is not None:
                    if not auth_user.is_superuser:
                        # get box researcher
                        box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
                        if box_researcher is not None:
                            user = get_object_or_404(User, pk=box_researcher.researcher_id)
                            obj = {'user': user, 'container': container}
                            self.check_object_permissions(request, obj)  # check the permission
                            # switch position
                            sample1.vposition = second_pos[0]
                            sample1.hposition = second_pos[1]
                            sample2.vposition = first_pos[0]
                            sample2.hposition = first_pos[1]
                            sample1.save()
                            sample2.save()
                            return Response({'detail': 'sample position switched!'},
                                            status=status.HTTP_200_OK)
                        return Response({'detail': 'Permission denied!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # switch position
                        sample1.vposition = second_pos[0]
                        sample1.hposition = second_pos[1]
                        sample2.vposition = first_pos[0]
                        sample2.hposition = first_pos[1]
                        sample1.save()
                        sample2.save()
                        return Response({'detail': 'sample position switched!'},
                                        status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'at least one sample is not found, cannot switch the samples!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# switch samples between 2 boxes
class SwitchSample(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    @transaction.atomic
    def put(self, request):
        try:
            serializer = SwitchSampleBoxesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            auth_user = request.user
            #first container
            first_container_pk = data.get('first_container_pk', '')
            first_box_tower = data.get('first_box_tower', '')
            first_box_shelf = data.get('first_box_shelf', '')
            first_box_box = data.get('first_box_box', '')
            first_sample_vposition = data.get('first_sample_vposition', '')
            first_sample_hposition = data.get('first_sample_hposition', '')

            first_container = get_object_or_404(Container, pk=int(first_container_pk))
            first_box = BoxContainer.objects.all() \
                .filter(container_id=int(first_container_pk)) \
                .filter(tower=int(first_box_tower)) \
                .filter(shelf=int(first_box_shelf)) \
                .filter(box=int(first_box_box)) \
                .first()
            if first_box is None:
                return Response({'detail': 'first box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box researcher
            if not auth_user.is_superuser:
                first_box_researcher = BoxResearcher.objects.all().filter(box_id=first_box.pk).first()
                if first_box_researcher is not None:
                    # user = get_object_or_404(User, pk=first_box_researcher.researcher_id)
                    obj = {'user': auth_user, 'container': first_container}
                    self.check_object_permissions(request, obj)  # check the permission

            # second container
            second_container_pk = data.get('second_container_pk', '')
            second_box_tower = data.get('second_box_tower', '')
            second_box_shelf = data.get('second_box_shelf', '')
            second_box_box = data.get('second_box_box', '')
            second_sample_vposition = data.get('second_sample_vposition', '')
            second_sample_hposition = data.get('second_sample_hposition', '')

            second_container = get_object_or_404(Container, pk=int(second_container_pk))
            second_box = BoxContainer.objects.all() \
                .filter(container_id=int(second_container_pk)) \
                .filter(tower=int(second_box_tower)) \
                .filter(shelf=int(second_box_shelf)) \
                .filter(box=int(second_box_box)) \
                .first()
            if second_box is None:
                return Response({'detail': 'second box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            # box researcher
            if not auth_user.is_superuser:
                second_box_researcher = BoxResearcher.objects.all().filter(box_id=second_box.pk).first()
                if second_box_researcher is not None:
                    # user = get_object_or_404(User, pk=second_box_researcher.researcher_id)
                    obj = {'user': auth_user, 'container': second_container}
                    self.check_object_permissions(request, obj)  # check the permission

            # first sample
            first_sample = Sample.objects.all().filter(box_id=first_box.pk).filter(
                        vposition__iexact=first_sample_vposition).filter(
                        hposition=int(first_sample_hposition)).filter(occupied__iexact=1).first()
            # second sample
            second_sample = Sample.objects.all().filter(box_id=second_box.pk).filter(
                vposition__iexact=second_sample_vposition).filter(
                hposition=int(second_sample_hposition)).filter(occupied__iexact=1).first()
            if first_sample is None and second_sample is None:
                return Response({'detail': 'both samples are not found!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # switch box container pk
            first_box.container_id = second_container_pk
            first_box.save()
            second_box.container_id = first_container_pk
            second_box.save()

            if first_sample is not None:
                # switch sample box pk
                first_sample.box_id = second_box.pk
                first_sample.vposition = second_sample_vposition
                first_sample.hposition = second_sample_hposition
                first_sample.save()
            if second_sample is not None:
                second_sample.box_id = first_box.pk
                second_sample.vposition = first_sample_vposition
                second_sample.hposition = first_sample_hposition
                second_sample.save()
            return Response({'detail': 'sample positions switched!'},
                            status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# sample attachments
class SampleAttachmentListAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def get(self, request, ct_id, tw_id, sf_id, bx_id, sp_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # get the attachments
                        attachments = SampleAttachment.objects.all().filter(sample_id=sample.pk)
                        serializer = SampleAttachmentSerializer(attachments, many=True)
                        return Response(serializer.data)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, ct_id, tw_id, sf_id, bx_id, sp_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is not None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).filter(occupied__iexact=1).first()
                    if sample is not None:
                        # need to add attachment
                        serializer = SampleAttachmentSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        sample_attachment = SampleAttachment()
                        try:
                            sample_attachment = SampleAttachment.objects.create(
                                sample_id=sample.pk,
                                label=data.get("label", ""),
                                attachment=request.FILES['attachment'] if request.FILES and request.FILES['attachment'] else None,
                                description=data.get("description", "")
                            )
                        except:
                            if request.FILES and request.FILES['attachment']:
                                sample_attachment.attachment.delete()
                                return Response({'detail': 'Something went wrong, attachment not added!'},
                                                status=status.HTTP_400_BAD_REQUEST)
                        # sample_attachment = SampleAttachmentSerializer(**data)
                        # sample_attachment.save()
                        return Response({'detail': 'sample attachment saved!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


class SampleAttachmentList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def get(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
                        # get the attachments
                        attachments = SampleAttachment.objects.all().filter(sample_id=sample.pk)
                        serializer = SampleAttachmentSerializer(attachments, many=True)
                        return Response(serializer.data)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # need to add attachment
                        serializer = SampleAttachmentSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        sample_attachment = SampleAttachment()
                        try:
                            sample_attachment = SampleAttachment.objects.create(
                                sample_id=sample.pk,
                                label=data.get("label", ""),
                                attachment=request.FILES['attachment'] if request.FILES and request.FILES[
                                    'attachment'] else None,
                                description=data.get("description", "")
                            )
                        except:
                            if request.FILES and request.FILES['attachment']:
                                sample_attachment.attachment.delete()
                                return Response({'detail': 'Something went wrong, attachment not added!'},
                                                status=status.HTTP_400_BAD_REQUEST)
                        return Response({'detail': 'sample attachment saved!'},
                                        status=status.HTTP_200_OK)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


class SampleAttachmentDetailAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def get(self, request, ct_id, tw_id, sf_id, bx_id, sp_id, at_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # get the attachments
                        attachment = get_object_or_404(SampleAttachment, pk=at_id)
                        serializer = SampleAttachmentSerializer(attachment)
                        return Response(serializer.data)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ct_id, tw_id, sf_id, bx_id, sp_id, at_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # get the attachments
                        attachment = get_object_or_404(SampleAttachment, pk=at_id)
                        attachment.delete()
                        return Response({'detail': 'sample attachment deleted!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, ct_id, tw_id, sf_id, bx_id, sp_id, at_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # get the attachments
                        attachment = get_object_or_404(SampleAttachment, pk=at_id)
                        serializer = SampleAttachmentEditSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        attachment.label = data.get("label", "")
                        attachment.description = data.get("description", "")
                        if request.FILES and request.FILES['attachment'] and attachment.attachment:
                            attachment.attachment.delete()
                            attachment.attachment = request.FILES['attachment']
                        attachment.save()
                        return Response({'detail': 'sample attachment changed!'}, status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


class SampleAttachmentDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def get(self, request, ct_id, bx_id, sp_id, at_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        attachment = get_object_or_404(SampleAttachment, pk=at_id)
                        serializer = SampleAttachmentSerializer(attachment)
                        return Response(serializer.data)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ct_id, bx_id, sp_id, at_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        attachment = get_object_or_404(SampleAttachment, pk=at_id)
                        attachment.delete()
                        return Response({'detail': 'sample attachment deleted!'},
                                status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, ct_id, bx_id, sp_id, at_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # get the attachments
                        attachment = get_object_or_404(SampleAttachment, pk=at_id)
                        serializer = SampleAttachmentEditSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        attachment.label = data.get("label", "")
                        attachment.description = data.get("description", "")
                        if request.FILES and request.FILES['attachment'] and attachment.attachment:
                            attachment.attachment.delete()
                            attachment.attachment = request.FILES['attachment']
                        attachment.save()
                        return Response({'detail': 'sample attachment changed!'}, status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# sample taken out
class SampleTakeAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, ct_id, tw_id, sf_id, bx_id, sp_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).filter(occupied__iexact=1).first()
                    if sample is not None:
                        sample.occupied = False
                        sample.date_out = datetime.datetime.now()
                        sample.save()
                        return Response({'detail': 'sample is taken out!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


class SampleTake(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).filter(occupied__iexact=1).first()
                    if sample is not None:
                        sample.occupied = False
                        sample.date_out = datetime.datetime.now()
                        sample.save()
                        return Response({'detail': 'sample is taken out!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# put sample back
class SampleBackAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, ct_id, tw_id, sf_id, bx_id, sp_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).filter(occupied__iexact=0).first()
                    occuped_sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).filter(occupied__iexact=1).first()
                    if occuped_sample is not None:
                        return Response({'detail': 'slot has been occupied, failed to put sample back!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if sample is not None:
                        sample.occupied = True
                        sample.date_out = None
                        sample.save()
                        return Response({'detail': 'sample is put back!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


class SampleBack(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).filter(occupied__iexact=0).first()
                    occuped_sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).filter(occupied__iexact=1).first()
                    if occuped_sample is not None:
                        return Response({'detail': 'slot has been occupied, failed to put sample back!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if sample is not None:
                        sample.occupied = True
                        sample.date_out = None
                        sample.save()
                        return Response({'detail': 'sample is put back!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# change sample color
class SampleColorAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, ct_id, tw_id, sf_id, bx_id, sp_id):
        try:
            # get the container
            container = get_object_or_404(Container, pk=int(ct_id))
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
                # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # validate serializer
                        serializer = SampleColorSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        sample.color = data['color']
                        sample.save()
                        return Response({'detail': 'color is updated!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


class SampleColor(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, ct_id, bx_id, sp_id):
        try:
            container = get_object_or_404(Container, pk=int(ct_id))
            id_list = bx_id.split("-")
            tw_id = int(id_list[0])
            sf_id = int(id_list[1])
            bx_id = int(id_list[2])
            if int(tw_id) > int(container.tower) or int(tw_id) < 0:
                return Response({'detail': 'tower does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if int(sf_id) > int(container.shelf) or int(sf_id) < 0:
                return Response({'detail': 'shelf does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if int(bx_id) > int(container.box) or int(bx_id) < 0:
                return Response({'detail': 'Box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # box
            box = BoxContainer.objects.all() \
                .filter(container_id=int(ct_id)) \
                .filter(tower=int(tw_id)) \
                .filter(shelf=int(sf_id)) \
                .filter(box=int(bx_id)) \
                .first()
            if box is None:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher is not None:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {'user': user, 'container': container}
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample is not None:
                        # validate serializer
                        serializer = SampleColorSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        sample.color = data['color']
                        sample.save()
                        return Response({'detail': 'color is updated!'},
                                        status=status.HTTP_200_OK)
                return Response({'detail': 'sample does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# tags
class Tags(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:
            user = request.user
            # super user
            if user.is_superuser:
                serializer = SampleTagSerializer(SampleTag.objects.all(), many=True)
                return Response(serializer.data)
            # not the super user
            group_ids = []
            # I am a PI
            pi_groups = Group.objects.all().filter(email__iexact=user.email).distinct()
            if pi_groups is not None:
                group_ids = [g.pk for g in pi_groups]
            # get my groups
            my_groups = GroupResearcher.objects.all().filter(user_id=user.pk)
            if my_groups:
                my_group_ids = [g.group_id for g in my_groups]
                # combine 2 arrays
                group_ids = list(set(group_ids + my_group_ids))
            if group_ids:
                # get tags
                tags = SampleTag.objects.all().filter(group_id__in=group_ids).distinct()
                serializer = SampleTagSerializer(tags, many=True)
                return Response(serializer.data)
            else:
                serializer = SampleTagSerializer(SampleTag())
                return Response(serializer.data)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            serializer = SampleTagSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            tag = SampleTag(**data)
            tag.save()
            return Response({'detail': 'tag saved!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


# remove sample attachment
class DeleteAttachment(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def put(self, request, sp_id, at_id):
        try:
            auth_user = request.user
            sample = Sample.objects.all().filter(id=int(sp_id)).first()
            if sample is None:
                return Response({'detail': 'Sample not found!'},
                                status=status.HTTP_400_BAD_REQUEST)

            attachment = SampleAttachment.objects.all().filter(id=int(at_id)).first()
            if attachment is None:
                return Response({'detail': 'Attachment not found!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if auth_user.is_superuser:
                attachment.delete()
                return Response({'detail': 'attachment deleted!'},
                                status=status.HTTP_200_OK)
            else:
                # sample researchers
                sample_researcher = SampleResearcher.objects.all().filter(sample_id=sample.pk).first()
                if sample_researcher is not None:
                    sample_user = get_object_or_404(User, pk=sample_researcher.researcher_id)
                    self.check_object_permissions(request, {'user': sample_user})  # check the permission
                    attachment.delete()
                    return Response({'detail': 'attachment deleted!'},
                                    status=status.HTTP_200_OK)
                return Response({'detail': 'Permission denied!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# upload attachment to a sample
class UploadAttachment(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def post(self, request, sp_id):
        has_attachment = False
        sample_attachment = SampleAttachment()
        try:
            user = request.user
            # parse data
            form_data = dict(request.data)
            # check upload photo
            if 'file' in form_data.keys():
                has_attachment = True
            # form model data
            model = form_data['obj'][0]
            # load into dict
            obj = json.loads(model)
            serializer = UploadAttacgmentSerializer(data=obj)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            sample_attachment.label = data.get("label", "")
            sample_attachment.description = data.get("description", "")
            sample = get_object_or_404(Sample, pk=sp_id)
            if sample is not None:
                sample_attachment.sample = sample
                # save attachment
                sample_attachment.attachment = form_data['file'][0]
                # check permission
                if user.is_superuser:
                    sample_attachment.save()
                else:
                    # sample researchers
                    sample_researcher = SampleResearcher.objects.all().filter(sample_id=sample.pk).first()
                    if sample_researcher is not None:
                        sample_user = get_object_or_404(User, pk=sample_researcher.researcher_id)
                        self.check_object_permissions(request, {'user': sample_user})  # check the permission
                    sample_attachment.save()
                # return the new attachment
                # SampleAttachmentSerializer
                serializer = SampleAttachmentSerializer(sample_attachment)
                return Response(serializer.data)
            return Response({'detail': 'sample not found!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            if has_attachment and sample_attachment.attachment is not None:
                sample_attachment.attachment.delete()
            return Response({'detail': 'Something went wrong, sample attachment not uploaded!'},
                            status=status.HTTP_400_BAD_REQUEST)


# search samples
class SearchSamples(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, )

    def post(self, request):
        try:
            serializer = SearchSampleSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            # generate kwargs

            # container
            container = data.get('container', -1)
            type = data.get('type', 'GENERAL')
            occupied = data.get('occupied', 0)

            kwargs = {}

            if container != -1:
                kwargs["box__container_id__exact"] = container
            if type is not None:
                kwargs["type__iexact"] = type
            if occupied == 0:
                kwargs["occupied__iexact"] = 1
            if occupied == 1:
                kwargs["occupied__iexact"] = 0
            name = data.get('name', "")
            if name is not None:
                kwargs["name__icontains"] = name

            label = data.get('label', '')
            if label is not None:
                kwargs["label__icontains"] = label

            tag = data.get('tag', '')
            if tag is not None:
                kwargs["tag__icontains"] = tag

            freezing_date_from = data.get('freezing_date_from', "")
            if freezing_date_from is not None:
                kwargs["freezing_date__gte"] = freezing_date_from

            freezing_date_to = data.get('freezing_date_to', "")
            if freezing_date_to is not None:
                kwargs["freezing_date__lte"] = freezing_date_to

            registration_code = data.get('registration_code', "")
            if registration_code is not None:
                kwargs["registration_code__icontains"] = registration_code

            freezing_code = data.get('freezing_code', "")
            if freezing_code is not None:
                kwargs["freezing_code__icontains"] = freezing_code

            reference_code = data.get('reference_code', "")
            if reference_code is not None:
                kwargs["reference_code__icontains"] = reference_code

            # tissue
            pathology_code = data.get('pathology_code', "")
            if pathology_code is not None:
                kwargs["pathology_code__icontains"] = pathology_code

            tissue = data.get('tissue', "")
            if tissue is not None:
                kwargs["tissue__icontains"] = tissue

            # (gRNA) Oligo only
            oligo_name = data.get('oligo_name', "")
            if oligo_name is not None:
                kwargs["oligo_name__icontains"] = oligo_name

            oligo_length_from = data.get('oligo_length_from', "")
            if oligo_length_from is not None:
                kwargs["oligo_length__gte"] = oligo_length_from

            oligo_length_to = data.get('oligo_length_to', "")
            if oligo_length_to is not None:
                kwargs["oligo_length__lte"] = oligo_length_to

            # construct only
            feature = data.get('feature', "")
            if feature is not None:
                kwargs["feature__icontains"] = feature

            backbone = data.get('backbone', "")
            if backbone is not None:
                kwargs["backbone__icontains"] = backbone

            insert = data.get('insert', "")
            if insert is not None:
                kwargs["insert__icontains"] = insert

            marker = data.get('marker', "")
            if marker is not None:
                kwargs["marker__icontains"] = marker

            # virus
            plasmid = data.get('plasmid', "")
            if plasmid is not None:
                kwargs["plasmid__icontains"] = plasmid

            titration_code = data.get('titration_code', "")
            if titration_code is not None:
                kwargs["titration_code__icontains"] = titration_code
            samples = Sample.objects.filter(**kwargs)
            serializer = SampleSerializer(samples, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong, search is not performed!'},
                            status=status.HTTP_400_BAD_REQUEST)