from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *

from groups.models import Group, GroupResearcher
from api.permissions import IsPIorAssistantofUserOrReadOnly
from api.users.serializers import UserSerializer

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
            return Response({'detail': 'group added!'}, status=status.HTTP_200_OK)
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
        if group.groupresearcher_set:
            return Response({'detail': 'group not deleted! The group contains researcher(s).'}, status=status.HTTP_400_BAD_REQUEST)
        if group.groupcontainer_set:
            return Response({'detail': 'group not deleted! The group contains container(s).'},
                            status=status.HTTP_400_BAD_REQUEST)
        group.delete()
        return Response({'detail': 'group deleted!'}, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        group = get_object_or_404(Group, pk=pk)
        serializer = GroupDetailCreateSerializer(group, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'group details changed!'}, status=status.HTTP_200_OK)


# ====================================================
#  PI needs add researcher to a group
# ====================================================
class GroupResearcherList(APIView):

    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUserOrReadOnly,)

    # get the list of current user with role
    def get(self, request, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
            # get my groups
            my_groups = GroupResearcher.objects.all().filter(user_id=user.pk)
            if my_groups:
                my_group_ids = [g.group_id for g in my_groups]
                researchers = User.objects.all().filter(groupresearcher__group_id__in=my_group_ids)
                serializer = UserSerializer(researchers, many=True)
                return Response(serializer.data)
            return Response({'detail': 'no researcher in the group'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
            serializer = GroupResearcherCreateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            group_researcher = GroupResearcher(**data)
            group_researcher.save()
            return Response({'detail': 'researcher added to the group!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'researcher not added to the group!'}, status=status.HTTP_400_BAD_REQUEST)


# researcher details
class GroupResearcherDetail(APIView):

    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUserOrReadOnly,)

    def get(self, request, pk, format=None):
        try:
            user = request.user
            obj = {'user': user}
            self.check_object_permissions(request, obj)  # check the permission
            # get my groups
            my_groups = GroupResearcher.objects.all().filter(user_id=user.pk)
            if my_groups:
                my_group_ids = [g.group_id for g in my_groups]
                researcher = User.objects.all().filter(groupresearcher__group_id__in=my_group_ids).filter(pk=pk).first()
                if researcher:
                    serializer = UserSerializer(researcher)
                    return Response(serializer.data)
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        user = request.user
        obj = {'user': user}
        self.check_object_permissions(request, obj)  # check the permission
        pass

    def delete(self, request, pk, format=None):
        pass


