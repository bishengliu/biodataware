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
import re
import datetime


# all container list only for manager or admin
# for admin and manager get all the conatiners, otherwise only show current group containers
class ContainerList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly, )

    def get(self, request, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        # filter the containers for the pi or assistant
        # show all the containers if pi or assistant is also the manager
        try:
            if user.is_superuser:
                containers = Container.objects.all()
                serializer = ConatainerSerializer(containers, many=True)
                return Response(serializer.data)
            else:
                # get the group id of the current user
                groupresearchers = GroupResearcher.object.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                containers = Container.objects.all().fillter(groupcontainer_set__group_id__in=group_ids)
            serializer = ConatainerSerializer(containers, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        try:
            if user.is_superuser:
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
                # save the container
                container = Container()
                name = data.get("name", "")
                room = data.get("room", "")
                temperature = data.get("temperature", "")
                tower = data.get("tower", 1)
                shelf = data.get("shelf", 1)
                box = data.get("box", 1)
                description = data.get("description", "")

                try:
                    container = Container.objects.create(
                        name=name,
                        room=room,
                        temperature=temperature,
                        tower=tower,
                        shelf=shelf,
                        box=box,
                        description=description,
                        photo=request.FILES['photo'] if request.FILES and request.FILES['photo'] else None
                    )
                    # add container to groups
                    for group_id in group_ids:
                        GroupContainer.objects.create(
                            container_id=container.pk,
                            group_id=group_id
                        )
                    return Response({'detail': 'container added!'}, status=status.HTTP_200_OK)
                except:
                    if request.FILES and request.FILES['photo']:
                        container.photo.delete()
                    return Response({'detail': 'Something went wrong, container not added!'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong, container not added!'},
                            status=status.HTTP_400_BAD_REQUEST)


# view, edit and delete container
class ContainerDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly, )

    def get(self, request, pk, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
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
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        container = get_object_or_404(Container, pk=pk)
        try:
            if user.is_superuser:
                serializer = ContainerUpdateSerializer(container, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                data = serializer.data
                #serializer.save()
                # save the container
                container.name = data.get("name", "")
                container.room = data.get("room", "")
                container.temperature = data.get("temperature", "")
                container.tower = data.get("tower", 1)
                container.shelf = data.get("shelf", 1)
                container.box = data.get("box", 1)
                container.description = data.get("description", "")
                if request.FILES and request.FILES['photo'] and container.photo:
                    container.photo.delete()
                    container.photo = request.FILES['photo']
                container.save()
                return Response({'detail': 'container info changed!'}, status=status.HTTP_200_OK)
                #return Response(ConatainerSerializer(container).data)
            else:
                # check which group has/have the container
                group_containers = GroupContainer.objects.all().filter(container_id=container.pk)
                if group_containers:
                    group_container_ids = [gc.group_id for gc in group_containers]
                    # is pi/assistant of the group
                    if isPIorAssistantofGroup(user, group_container_ids):
                        # save data
                        serializer = ContainerUpdateSerializer(container, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        # serializer.save()
                        # save the container
                        container.name = data.get("name", "")
                        container.room = data.get("room", "")
                        container.temperature = data.get("temperature", "")
                        container.tower = data.get("tower", 1)
                        container.shelf = data.get("shelf", 1)
                        container.box = data.get("box", 1)
                        container.description = data.get("description", "")
                        if request.FILES and request.FILES['photo'] and container.photo:
                            container.photo.delete()
                            container.photo = request.FILES['photo']
                        container.save()
                        return Response({'detail': 'container info changed!'}, status=status.HTTP_200_OK)
                return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'container info not changed!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
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
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly, )

    def get(self, request, ct_id, format=None):
        user = request.user
        obj = {
            'user': user
        }
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
        obj = {
            'user': user
        }
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

    def get(self, request, ct_id,  pk, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        group_container = get_object_or_404(GroupContainer, pk= pk)
        serializer = GroupContainerSerializer(group_container)
        return Response(serializer.data)

    def delete(self, request, ct_id, pk, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
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
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
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
            serializer = BoxContainerSerializer(boxes, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, ct_id, tw_id, sf_id, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
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
            if bc:
                return Response({'detail': 'box already exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box_container = BoxContainer.objects.create(
                container_id=int(ct_id),
                box_vertical=data['box_vertical'],
                box_horizontal=data['box_horizontal'],
                tower=int(tw_id),
                shelf=int(sf_id),
                box=data['box']
            )
            box_researcher = BoxResearcher.objects.create(
                box_id=box_container.pk,
                researcher_id=user.pk
            )
            return Response({'detail': 'Box add!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Box not added!'},
                            status=status.HTTP_400_BAD_REQUEST)


class Shelf(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def get(self, request, ct_id, id, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
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
        serializer = BoxContainerSerializer(boxes, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, ct_id, id, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
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
            if bc:
                return Response({'detail': 'box already exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box_container = BoxContainer.objects.create(
                container_id=int(ct_id),
                box_vertical=data['box_vertical'],
                box_horizontal=data['box_horizontal'],
                tower=int(tw_id),
                shelf=int(sf_id),
                box=data['box']
            )
            box_researcher = BoxResearcher.objects.create(
                box_id=box_container.pk,
                researcher_id=user.pk
            )
            return Response({'detail': 'Box add!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Box not added!'},
                                status=status.HTTP_400_BAD_REQUEST)


# boxes list of a container, quick access
class ContainerBoxList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def get(self, request, ct_id, format=None):
        user = request.user
        # get the container
        container = get_object_or_404(Container, pk=ct_id)
        obj = {
            'user': user,
            'container': container
        }
        self.check_object_permissions(request, obj)  # check the permission
        try:
            # get the boxes
            if user.is_superuser:
                container = get_object_or_404(Container, pk=int(ct_id))
                boxes = BoxContainer.objects.all().filter(container_id=container.pk)
                serializer = BoxContainerSerializer(boxes, many=True)
                return Response(serializer.data)
            else:
                # get only the boxes of the group(s)
                # get the current group id
                groupresearchers = GroupResearcher.object.all().filter(user_id=user.pk)
                group_ids = [g.group_id for g in groupresearchers]
                container = get_object_or_404(Container, pk=int(ct_id))
                boxes = BoxContainer.objects.all().filter(container_id=container.pk).filter(
                    boxresearcher_set__researcher_id__in=group_ids)
                serializer = BoxSamplesSerializer(boxes, many=True)
                return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, ct_id, format=None):
        user = request.user
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        # get the container
        container = get_object_or_404(Container, pk=int(ct_id))
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
            if bc:
                return Response({'detail': 'box already exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box_container = BoxContainer.objects.create(
                container_id=int(ct_id),
                box_vertical=data['box_vertical'],
                box_horizontal=data['box_horizontal'],
                tower=int(tw_id),
                shelf=int(sf_id),
                box=data['box']
            )

            box_researcher = BoxResearcher.objects.create(
                box_id=box_container.pk,
                researcher_id=user.pk
            )
            return Response({'detail': 'Box add!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Box not added!'},
                            status=status.HTTP_400_BAD_REQUEST)


# ==============================================================
# allow view and add samples
# box and sample list
# =====================================
# need to apply permissions to only allow view the box details in the group
class BoxAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

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
                obj = {
                    'user': user
                }
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
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
                obj = {
                    'user': user
                }
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
                    description=data.get('description', '')
                )
                # save sample tissue
                # separated by '-'
                if data.get('system', "") != "" and data.get('tissue', "") != "":
                    # parse system
                    if "-" in data.get('system', ""):
                        system_list = data.get('system', "").split("-")
                        if "-" in data.get('tissue', ""):
                            tissue_list = data.get('tissue', "").split("-")
                            if len(system_list) == len(tissue_list):
                                # create object
                                for s in list(range(len(system_list))):
                                    # validate the system
                                    if get_object_or_404(Biosystem, pk=int(system_list[s])):
                                        if "," in tissue_list[s]:
                                            tissue_ids = tissue_list[s].split(",")
                                            for t in list(range(len(tissue_ids))):
                                                # validate tissue
                                                if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                                    SampleTissue.objects.create(
                                                        sample_id=sample.pk,
                                                        system_id=int(system_list[s]),
                                                        tissue_id=int(tissue_ids[t])
                                                    )
                                        else:
                                            # validate tissue
                                            if get_object_or_404(Tissue, pk=int(tissue_list[s])):
                                                SampleTissue.objects.create(
                                                    sample_id=sample.pk,
                                                    system_id=int(system_list[s]),
                                                    tissue_id=int(tissue_list[s])
                                                )
                    else:
                        system_id = int(data.get('system', ""))
                        if get_object_or_404(Biosystem, pk=system_id):
                            if "-" not in data.get('tissue', ""):
                                tissue_id = data.get('tissue', "")
                                if "," in tissue_id:
                                    tissue_ids = tissue_id.split(",")
                                    for t in list(range(len(tissue_ids))):
                                        # validate tissue
                                        if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                            SampleTissue.objects.create(
                                                sample_id=sample.pk,
                                                system_id=system_id,
                                                tissue_id=int(tissue_ids[t])
                                            )
                                else:
                                    # validate tissue
                                    if get_object_or_404(Tissue, pk=int(tissue_id)):
                                        SampleTissue.objects.create(
                                            sample_id=sample.pk,
                                            system_id=system_id,
                                            tissue_id=int(tissue_id)
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
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier, IsPIorAssistantorOwner,)

    def get(self, request, ct_id, id, format=None):
        try:
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
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                serializer = BoxSamplesSerializer(box)
                return Response(serializer.data)
            return Response({'detail': 'Permission denied!'},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Something went wrong!'},
                    status=status.HTTP_400_BAD_REQUEST)

    # delete box
    def delete(self, request, ct_id, id, format=None):
        try:
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
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
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
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                serializer = SampleCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                data = serializer.data
                # check whether the position of the sample has already be occupied
                if Sample.objects.all().filter(box_id=box.pk).filter(hposition=data.get("hposition", "")).filter(
                        vposition=data.get("vposition", "")).filter(occupied=True):
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
                    description=data.get('description', '')
                )
                # save sample tissue
                # separated by '-'
                if data.get('system', "") != "" and data.get('tissue', "") != "":
                    # parse system
                    if "-" in data.get('system', ""):
                        system_list = data.get('system', "").split("-")
                        if "-" in data.get('tissue', ""):
                            tissue_list = data.get('tissue', "").split("-")
                            if len(system_list) == len(tissue_list):
                                # create object
                                for s in list(range(len(system_list))):
                                    # validate the system
                                    if get_object_or_404(Biosystem, pk=int(system_list[s])):
                                        if "," in tissue_list[s]:
                                            tissue_ids = tissue_list[s].split(",")
                                            for t in list(range(len(tissue_ids))):
                                                # validate tissue
                                                if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                                    SampleTissue.objects.create(
                                                        sample_id=sample.pk,
                                                        system_id=int(system_list[s]),
                                                        tissue_id=int(tissue_ids[t])
                                                    )
                                        else:
                                            # validate tissue
                                            if get_object_or_404(Tissue, pk=int(tissue_list[s])):
                                                SampleTissue.objects.create(
                                                    sample_id=sample.pk,
                                                    system_id=int(system_list[s]),
                                                    tissue_id=int(tissue_list[s])
                                                )
                    else:
                        system_id = int(data.get('system', ""))
                        if get_object_or_404(Biosystem, pk=system_id):
                            if "-" not in data.get('tissue', ""):
                                tissue_id = data.get('tissue', "")
                                if "," in tissue_id:
                                    tissue_ids = tissue_id.split(",")
                                    for t in list(range(len(tissue_ids))):
                                        # validate tissue
                                        if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                            SampleTissue.objects.create(
                                                sample_id=sample.pk,
                                                system_id=system_id,
                                                tissue_id=int(tissue_ids[t])
                                            )
                                else:
                                    # validate tissue
                                    if get_object_or_404(Tissue, pk=int(tissue_id)):
                                        SampleTissue.objects.create(
                                            sample_id=sample.pk,
                                            system_id=system_id,
                                            tissue_id=int(tissue_id)
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
                                    attachment=request.FILES['attachment' + str(l)] if (
                                    request.FILES and request.FILES['attachment' + str(l)]) else None
                                )
                    else:
                        SampleAttachment.objects.create(
                            sample_id=sample.pk,
                            label=data.get('label', ""),
                            description=data.get("attachment_description", ""),
                            attachment=request.FILES['attachment'] if (
                            request.FILES and request.FILES['attachment']) else None
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


# get, put and delete sample
class SampleDetailAlternative(APIView):
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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

    @transaction.atomic
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
                        serializer = SampleEditSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        # sample info
                        sample.color = data.get('color', '#EEEEEE')
                        sample.name = data['name']
                        sample.freezing_date = data.get('freezing_date', datetime.datetime.now())
                        sample.registration_code = data.get('registration_code', '')
                        sample.pathology_code = data.get('pathology_code', '')
                        sample.freezing_code = data.get('freezing_code', '')
                        sample.quantity = data['quantity']
                        sample.type = data.get('type', '')
                        sample.description = data.get('description', '')
                        sample.save()
                        # save sample tissue
                        # separated by '-'
                        if data.get('system', "") != "" and data.get('tissue', "") != "":
                            # delete old tissue
                            old_tissues = SampleTissue.objects.all().filter(sample_id=sample.pk)
                            if old_tissues:
                                for t in old_tissues:
                                    t.delete()
                            # parse system
                            if "-" in data.get('system', ""):
                                system_list = data.get('system', "").split("-")
                                if "-" in data.get('tissue', ""):
                                    tissue_list = data.get('tissue', "").split("-")
                                    if len(system_list) == len(tissue_list):
                                        # create object
                                        for s in list(range(len(system_list))):
                                            # validate the system
                                            if get_object_or_404(Biosystem, pk=int(system_list[s])):
                                                if "," in tissue_list[s]:
                                                    tissue_ids = tissue_list[s].split(",")
                                                    for t in list(range(len(tissue_ids))):
                                                        # validate tissue
                                                        if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                                            SampleTissue.objects.create(
                                                                sample_id=sample.pk,
                                                                system_id=int(system_list[s]),
                                                                tissue_id=int(tissue_ids[t])
                                                            )
                                                else:
                                                    # validate tissue
                                                    if get_object_or_404(Tissue, pk=int(tissue_list[s])):
                                                        SampleTissue.objects.create(
                                                            sample_id=sample.pk,
                                                            system_id=int(system_list[s]),
                                                            tissue_id=int(tissue_list[s])
                                                        )
                            else:
                                system_id = int(data.get('system', ""))
                                if get_object_or_404(Biosystem, pk=system_id):
                                    if "-" not in data.get('tissue', ""):
                                        tissue_id = data.get('tissue', "")
                                        if "," in tissue_id:
                                            tissue_ids = tissue_id.split(",")
                                            for t in list(range(len(tissue_ids))):
                                                # validate tissue
                                                if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                                    SampleTissue.objects.create(
                                                        sample_id=sample.pk,
                                                        system_id=system_id,
                                                        tissue_id=int(tissue_ids[t])
                                                    )
                                        else:
                                            # validate tissue
                                            if get_object_or_404(Tissue, pk=int(tissue_id)):
                                                SampleTissue.objects.create(
                                                    sample_id=sample.pk,
                                                    system_id=system_id,
                                                    tissue_id=int(tissue_id)
                                                )
                        # save sample researcher
                        if data.get('researcher', "") != "":
                            # delete old_researchers
                            old_researchers = SampleResearcher.objects.all().filter(sample_id=sample.pk)
                            if old_researchers:
                                for r in old_researchers:
                                    r.delete()
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


# get, put and delete sample
class SampleDetail(APIView):
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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

    @transaction.atomic
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
                        serializer = SampleEditSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        data = serializer.data
                        # sample info
                        sample.color = data.get('color', '#EEEEEE')
                        sample.name = data['name']
                        sample.freezing_date = data.get('freezing_date', datetime.datetime.now())
                        sample.registration_code = data.get('registration_code', '')
                        sample.pathology_code = data.get('pathology_code', '')
                        sample.freezing_code = data.get('freezing_code', '')
                        sample.quantity = data['quantity']
                        sample.type = data.get('type', '')
                        sample.description = data.get('description', '')
                        sample.save()
                        # save sample tissue
                        # separated by '-'
                        if data.get('system', "") != "" and data.get('tissue', "") != "":
                            # delete old tissue
                            old_tissues = SampleTissue.objects.all().filter(sample_id=sample.pk)
                            if old_tissues:
                                for t in old_tissues:
                                    t.delete()
                            # parse system
                            if "-" in data.get('system', ""):
                                system_list = data.get('system', "").split("-")
                                if "-" in data.get('tissue', ""):
                                    tissue_list = data.get('tissue', "").split("-")
                                    if len(system_list) == len(tissue_list):
                                        # create object
                                        for s in list(range(len(system_list))):
                                            # validate the system
                                            if get_object_or_404(Biosystem, pk=int(system_list[s])):
                                                if "," in tissue_list[s]:
                                                    tissue_ids = tissue_list[s].split(",")
                                                    for t in list(range(len(tissue_ids))):
                                                        # validate tissue
                                                        if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                                            SampleTissue.objects.create(
                                                                sample_id=sample.pk,
                                                                system_id=int(system_list[s]),
                                                                tissue_id=int(tissue_ids[t])
                                                            )
                                                else:
                                                    # validate tissue
                                                    if get_object_or_404(Tissue, pk=int(tissue_list[s])):
                                                        SampleTissue.objects.create(
                                                            sample_id=sample.pk,
                                                            system_id=int(system_list[s]),
                                                            tissue_id=int(tissue_list[s])
                                                        )
                            else:
                                system_id = int(data.get('system', ""))
                                if get_object_or_404(Biosystem, pk=system_id):
                                    if "-" not in data.get('tissue', ""):
                                        tissue_id = data.get('tissue', "")
                                        if "," in tissue_id:
                                            tissue_ids = tissue_id.split(",")
                                            for t in list(range(len(tissue_ids))):
                                                # validate tissue
                                                if get_object_or_404(Tissue, pk=int(tissue_ids[t])):
                                                    SampleTissue.objects.create(
                                                        sample_id=sample.pk,
                                                        system_id=system_id,
                                                        tissue_id=int(tissue_ids[t])
                                                    )
                                        else:
                                            # validate tissue
                                            if get_object_or_404(Tissue, pk=int(tissue_id)):
                                                SampleTissue.objects.create(
                                                    sample_id=sample.pk,
                                                    system_id=system_id,
                                                    tissue_id=int(tissue_id)
                                                )
                        # save sample researcher
                        if data.get('researcher', "") != "":
                            # delete old_researchers
                            old_researchers = SampleResearcher.objects.all().filter(sample_id=sample.pk)
                            if old_researchers:
                                for r in old_researchers:
                                    r.delete()
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
                        sample.occupied = True
                        sample.date_out = datetime.datetime.now()
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
                        sample.occupied = True
                        sample.date_out = datetime.datetime.now()
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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
            if not box:
                return Response({'detail': 'box does not exist!'},
                                status=status.HTTP_400_BAD_REQUEST)
            # get box researcher
            box_researcher = BoxResearcher.objects.all().filter(box_id=box.pk).first()
            if box_researcher:
                user = get_object_or_404(User, pk=box_researcher.researcher_id)
                obj = {
                    'user': user
                }
                self.check_object_permissions(request, obj)  # check the permission
                # find the sample
                match = re.match(r"([a-z]+)([0-9]+)", sp_id, re.I)
                if match:
                    pos = match.groups()
                    sample = Sample.objects.all().filter(box_id=box.pk).filter(vposition__iexact=pos[0]).filter(
                        hposition=pos[1]).first()
                    if sample:
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

