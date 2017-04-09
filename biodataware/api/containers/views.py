from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *
from helpers.acl import isManger, isInGroups, isPIorAssistantofGroup
from django.db import transaction
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from groups.models import Group, GroupResearcher
from api.permissions import IsInGroupContanier, IsPIorReadOnly


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
    permission_classes = (permissions.IsAuthenticated, )

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
    permission_classes = (permissions.IsAuthenticated,)

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


# box and sample list
# =====================================
# need to apply permissions to only allow view the box details in the group
class BoxAlternative(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def get(self, request, ct_id, tw_id, sf_id, bx_id, format=None):
        try:
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
            serializer = BoxSamplesSerializer(box)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # delete box
    def delete(self, request, ct_id, tw_id, sf_id, bx_id, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
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
            # check samples
            if box.sample_set:
                return Response({'detail': 'Cannot delete this box, there are samples in the box!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box.delete()
            return Response({'detail': 'Box deleted!'},
                            status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong!'},
                     status=status.HTTP_400_BAD_REQUEST)


# box and sample list
class Box(APIView):
    permission_classes = (permissions.IsAuthenticated, IsInGroupContanier,)

    def get(self, request, ct_id, id, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
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
            serializer = BoxSamplesSerializer(box)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)

    # delete box
    def delete(self, request, ct_id, id, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
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
            # check samples
            if box.sample_set:
                return Response({'detail': 'Cannot delete this box, there are samples in the box!'},
                                status=status.HTTP_400_BAD_REQUEST)
            box.delete()
            return Response({'detail': 'Box deleted!'},
                            status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong!'},
                            status=status.HTTP_400_BAD_REQUEST)


# samples
class SampleDetail(APIView):
    pass


class SampleDetailAlternative(APIView):
    pass