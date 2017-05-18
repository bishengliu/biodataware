from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from .serializers import *
from containers.models import GroupContainer
from groups.models import Group, GroupResearcher, Assistant
from api.permissions import IsPIorAssistantofUserOrReadOnly, IsPIorReadOnly, IsPI
from api.users.serializers import UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json


# for admin
# group list
class GroupList(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            user = request.user
            obj = {'user': user}
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
            serializer = GroupUpdateSerializer(data=obj, partial=True)
            serializer.is_valid(raise_exception=True)
            # save data
            data = serializer.data
            # create group
            group = Group()
            group.group_name = data.get('group_name')
            group.pi = data.get('pi')
            group.pi_fullname = data.get('pi_fullname')
            group.email = data.get('email')
            group.telephone = data.get('telephone', '')
            group.department = data.get('department', '')
            if has_photo:
                    group.photo = form_data['file'][0]
            group.save()
            return Response({'detail': True}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'group not added!'}, status=status.HTTP_400_BAD_REQUEST)


# group count
class GroupCount(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, format=None):
        group_count = Group.objects.all().count()
        return Response({'count': group_count}, status=status.HTTP_200_OK)


class GroupDetail(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, pk, format=None):
        group = get_object_or_404(Group, pk=pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        group = get_object_or_404(Group, pk=pk)
        try:
            group_researchers = GroupResearcher.objects.all().filter(group_id=group.pk)
            if group_researchers:
                return Response({'detail': 'group not deleted! The group contains researcher(s).'},
                                status=status.HTTP_400_BAD_REQUEST)
            group_containers = GroupContainer.objects.all().filter(group_id=group.pk)
            if group_containers:
                return Response({'detail': 'group not deleted! The group contains container(s).'},
                                status=status.HTTP_400_BAD_REQUEST)
            group.delete()
            return Response({'detail': 'group deleted!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'Something went wrong, group not deleted!'}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk, format=None):
        try:
            group = get_object_or_404(Group, pk=pk)

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
            serializer = GroupUpdateSerializer(data=obj, partial=False)
            serializer.is_valid(raise_exception=True)
            # save data
            data = serializer.data

            group.group_name = data.get('group_name')
            group.pi = data.get('pi')
            group.pi_fullname = data.get('pi_fullname')
            group.email = data.get('email')
            group.telephone = data.get('telephone', '')
            group.department = data.get('department', '')
            if has_photo:
                if group.photo:
                    group.photo.delete()
                group.photo = form_data['file'][0]
            group.save()
            return Response({'detail': True}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'group not updated!'}, status=status.HTTP_400_BAD_REQUEST)


# for PI
# ====================================================
#  PI needs add researcher to a group
# ====================================================
# edit group info by PI
class MyGroupUpdate(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated, IsPI)

    def put(self, request, format=None):

        try:
            user = request.user
            # group
            group = Group.objects.all().filter(email__iexact=user.email).first()
            obj = {'user': user}
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
            serializer = GroupUpdateSerializer(data=obj, partial=True)
            serializer.is_valid(raise_exception=True)
            # save data
            data = serializer.data

            group.group_name = data.get('group_name')
            group.pi = data.get('pi')
            group.pi_fullname = data.get('pi_fullname')
            group.email = data.get('email')
            group.telephone = data.get('telephone', '')
            group.department = data.get('department', '')
            if has_photo:
                if group.photo:
                    group.photo.delete()
                    group.photo = form_data['file'][0]
            group.save()
            return Response({'detail': True}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


# list all my groups
class MyGroupList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUserOrReadOnly,)

    def get(self, request, format=None):
        try:
            user = request.user
            obj = {'user': user}
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
            obj = {'user': user}
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


# for one group
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
            obj = {'user': user}
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
            obj = {'user': user}
            self.check_object_permissions(request, obj)  # check the permission
            serializer = GroupResearcherCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            group = get_object_or_404(Group, pk=data.get("group_id"))
            if group and int(pk) == data.get("group_id"):
                if get_object_or_404(User, pk=data.get("user_id")):
                    # check researcher is not added before
                    if GroupResearcher.objects.all().filter(user_id=data.get("user_id")).filter(
                            group_id=data.get("group_id")).first():
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
            obj = {'user': user}
            self.check_object_permissions(request, obj)  # check the permission
            serializer = GroupResearcherCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            group = get_object_or_404(Group, pk=data.get("group_id"))
            if group and int(pk) == data.get("group_id"):
                # check user
                if get_object_or_404(User, pk=data.get("user_id")):
                    if Assistant.objects.all().filter(user_id=data.get("user_id")).filter(
                            group_id=data.get("group_id")).first():
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


# search user info
# {'query': 'group_name', 'value': value, 'group_id': -1 }
class GroupSearch(APIView):

    def post(self, request, format=None):
        key = request.data.get('query', '')
        value = request.data.get('value', '')
        group_id = int(request.data.get('group_pk', -1))
        try:
            groups = Group.objects.all()
            if group_id >= 0:
                groups = groups.exclude(pk=group_id)
            if key == 'group_name' and value:
                group = groups.filter(group_name__iexact=value).first()
                if group:
                    return Response({'matched': True, 'group': GroupSerializer(group).data})
            if key == 'email' and value:
                group = groups.filter(email__iexact=value).first()
                if group:
                    return Response({'matched': True, 'group': GroupSerializer(group).data})
            return Response({'matched': False, 'group': ''})
        except:
            return Response({'detail': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

