from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *

from groups.models import Group, GroupResearcher, Assistant
from api.permissions import IsPIorAssistantofUserOrReadOnly, IsPIorReadOnly
from api.users.serializers import UserSerializer

# for admin
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


# for PI
# ====================================================
#  PI needs add researcher to a group
# ====================================================
# list all my groups
class MyGroupList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUserOrReadOnly,)

    def get(self, request, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
            # pi groups
            group_ids = []
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
                groups = Group.objects.all().filter(pk__in=group_ids).distinct()
                serializer = GroupSerializer(groups, many=True)
                return Response(serializer.data)
            return Response({'detail': False}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


# list all the researchers in my groups
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
            # pi groups
            group_ids = []
            pi_groups = Group.objects.all().filter(email__iexact=user.email).distinct()
            if pi_groups:
                group_ids = [g.pk for g in pi_groups]
            # get my groups
            my_groups = GroupResearcher.objects.all().filter(user_id=user.pk)
            if my_groups:
                my_group_ids = [g.group_id for g in my_groups]
                # combine 2 arrays
                group_ids = list(set(group_ids + my_group_ids))
            if group_ids:
                researchers = User.objects.all().filter(groupresearcher__group_id__in=group_ids).distinct()
                serializer = UserSerializer(researchers, many=True)
                return Response(serializer.data)
            return Response({'detail': False}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
            serializer = GroupResearcherCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            # pi groups
            group_ids = []
            pi_groups = Group.objects.all().filter(email__iexact=user.email).distinct()
            if pi_groups:
                group_ids = [g.pk for g in pi_groups]
            # get my groups
            my_groups = GroupResearcher.objects.all().filter(user_id=user.pk)
            if my_groups:
                my_group_ids = [g.group_id for g in my_groups]
                # combine 2 arrays
                group_ids = list(set(group_ids + my_group_ids))
            if group_ids:
                if data.group_id not in group_ids:
                    return Response({'detail': 'researcher cannot be added to the group!'}, status=status.HTTP_400_BAD_REQUEST)
                # check researcher is not added before
                if GroupResearcher.objects.all().filter(user_id=data.user_id).filter(group_id=data.group_id).first():
                    return Response({'detail': 'researcher already in the group!'}, status=status.HTTP_400_BAD_REQUEST)
                group_researcher = GroupResearcher(**data)
                group_researcher.save()
                return Response({'detail': 'researcher added to the group!'}, status=status.HTTP_200_OK)
            return Response({'detail': 'you do not have research group yet!'},
                            status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'detail': False}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


# list all the researchers in one group
class OneGroupResearcherList(APIView):

    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUserOrReadOnly,)

    # get the list of current user with role
    def get(self, request, pk, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
            # get my groups
            my_group = GroupResearcher.objects.all().filter(user_id=user.pk).filter(group_id=pk).first()
            if my_group:
                researchers = User.objects.all().filter(groupresearcher__group_id=pk).distinct()
                serializer = UserSerializer(researchers, many=True)
                return Response(serializer.data)
            return Response({'detail': 'permission denied!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
            serializer = GroupResearcherCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            group = get_object_or_404(Group, pk=data.group_id)
            if group and pk == data.group_id:
                if get_object_or_404(User, pk=data.user_id):
                    # check researcher is not added before
                    if GroupResearcher.objects.all().filter(user_id=data.user_id).filter(
                            group_id=data.group_id).first():
                        return Response({'detail': 'researcher already in the group!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    group_researcher = GroupResearcher(**data)
                    group_researcher.save()
                    return Response({'detail': 'researcher added to the group!'}, status=status.HTTP_200_OK)
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'researcher not added to the group!'}, status=status.HTTP_400_BAD_REQUEST)


class OneGroupResearcherDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUserOrReadOnly,)

    def get(self, request, g_id, u_id, format=None):
        user = get_object_or_404(User, pk=u_id)
        group = get_object_or_404(Group, pk=g_id)
        try:
            obj = {'user': user}
            self.check_object_permissions(request, obj)  # check the permission
            auth_user = request.user
            my_groups = GroupResearcher.objects.all().filter(user_id=auth_user.pk)
            if my_groups:
                my_group_ids = [g.group_id for g in my_groups]
                if int(g_id) in my_group_ids:
                    researcher = get_object_or_404(User, pk=u_id)
                    group_researcher = GroupResearcher.objects.all().filter(user_id=user.pk).filter(group_id=group.pk)
                    if researcher and group_researcher is not None:
                        serializer = UserSerializer(researcher)
                        return Response(serializer.data)
            return Response({'detail': 'permission denied!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, g_id, u_id, format=None):
        try:
            user = get_object_or_404(User, pk=u_id)
            obj = {'user': user}
            self.check_object_permissions(request, obj)  # check the permission
            # get my groups
            auth_user = request.user
            my_groups = GroupResearcher.objects.all().filter(user_id=auth_user.pk)
            if my_groups:
                my_group_ids = [g.group_id for g in my_groups]
                if int(g_id) in my_group_ids:
                    group_researcher = GroupResearcher.objects.all().filter(user_id=u_id).filter(group_id=g_id).first()
                    if group_researcher:
                        group_researcher.delete()
                    return Response({'detail': 'user removed from the group!'}, status=status.HTTP_200_OK)
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


class OneGroupAssistantList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly,)

    def get(self, request, pk, format=None):
        try:
            user = request.user
            obj = {'user': user}
            self.check_object_permissions(request, obj)  # check the permission
            group = get_object_or_404(Group, pk=pk)
            if group:
                # get my groups
                my_groups = GroupResearcher.objects.all().filter(user_id=user.pk)
                if my_groups:
                    my_group_ids = [g.group_id for g in my_groups]
                    if int(pk) in my_group_ids:
                        assistants = Assistant.objects.all().filter(group_id=pk)
                        if assistants:
                            assistant_ids = [a.pk for a in assistants]
                            if len(assistant_ids):
                                researchers = User.objects.all().filter(pk__in=assistant_ids)
                                serializer = UserSerializer(researchers, many=True)
                                return Response(serializer.data)
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk, format=None):
        try:
            user = request.user
            obj = {
                'user': user
            }
            self.check_object_permissions(request, obj)  # check the permission
            serializer = GroupResearcherCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            group = get_object_or_404(Group, pk=data.group_id)
            if group and pk == data.group_id:
                # check user
                if get_object_or_404(User, pk=data.user_id):
                    if Assistant.objects.all().filter(user_id=data.user_id).filter(
                            group_id=data.group_id).first():
                        return Response({'detail': 'assistant already in the group!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    assistant = Assistant(**data)
                    assistant.save()
                    return Response({'detail': 'assistant added to the group!'}, status=status.HTTP_200_OK)
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


class OneGroupAssistantDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorReadOnly,)

    def get(self, request, g_id, u_id,  format=None):
        user = get_object_or_404(User, pk=u_id)
        group = get_object_or_404(Group, pk=g_id)
        try:
            assistant = Assistant.objects.all().filter(group_id=g_id).filter(user_id=u_id).first()
            if assistant is not None:
                obj = {'user': user}
                self.check_object_permissions(request, obj)  # check the permission
                auth_user = request.user
                # get my groups
                my_groups = GroupResearcher.objects.all().filter(user_id=auth_user.pk)
                if my_groups:
                    my_group_ids = [g.group_id for g in my_groups]
                    if int(g_id) in my_group_ids:
                        serializer = UserSerializer(user)
                        return Response(serializer.data)
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, g_id, u_id, format=None):
        user = get_object_or_404(User, pk=u_id)
        group = get_object_or_404(Group, pk=g_id)
        try:
            assistant = Assistant.objects.all().filter(group_id=g_id).filter(user_id=u_id).first()
            if assistant is not None:
                obj = {'user': user}
                self.check_object_permissions(request, obj)  # check the permission
                # get my groups
                auth_user = request.user
                my_groups = GroupResearcher.objects.all().filter(user_id=auth_user.pk)
                if my_groups:
                    my_group_ids = [g.group_id for g in my_groups]
                    if int(g_id) in my_group_ids:
                        assistant.delete()
                        return Response({'detail': 'assistant removed from the group!'}, status=status.HTTP_200_OK)
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

