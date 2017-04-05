from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from .serializers import *

from roles.models import Role
from users.models import UserRole
from api.users.serializers import UserRoleCreateSerializer


# role list
class RoleList(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, format=None):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    # add role
    def post(self, request, format=None):
        try:
            serializer = RoleSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            role = Role(**data)
            role.save()
            return Response({'detail': 'role added!'})
        except:
            return Response({'detail': 'role not added!'}, status=status.HTTP_400_BAD_REQUEST)


# role detail
class RoleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self,request, pk, format=None):
        role = get_object_or_404(Role, pk=pk)
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        try:
            role = Role.objects.get(pk=pk)
            # check whether there are users with role
            researchers = UserRole.objects.all().filter(role_id=role.pk)
            if not researchers:
                role.delete()
                return Response({'detail': _('role is deleted!')})
            return Response({'detail': _('there are researchers with the current role, role can not be deleted!')}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': _('role is not deleted!')}, status=status.HTTP_400_BAD_REQUEST)


# User Role list
# only PI and Manager
class PIList(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get_view_name(self):
        return _('PI List')

    def get(self, request, format=None):
        try:
            # find the manger or pi role id
            role = Role.objects.all().filter(role__iexact='PI')
            userroles = UserRole.objects.all().filter(role_id__in=role.pk)
            serializer = PIManagerSerializer(userroles, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'fail to retrieve user roles!'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            serializer = UserRoleCreateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            # find the manger or pi role id
            role = Role.objects.all().filter(role__iexact='PI').first()
            if int(data['role_id']) != role.pk:
                return Response({'detail': 'user can only PI!'}, status=status.HTTP_400_BAD_REQUEST)
            userrole = UserRole(**data)
            userrole.save()
            return Response(serializer.data)
        except:
            return Response({'detail': 'user not added to the role!'}, status=status.HTTP_400_BAD_REQUEST)


class PIDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get_view_name(self):
        return _('PI Details')

    def get(self, request, pk, format=None):
        userrole = get_object_or_404(UserRole, pk=pk)
        serializer = PIManagerSerializer(userrole)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        userrole = get_object_or_404(UserRole, pk=pk)
        userrole.delete()
        return Response({'detail': 'user role deleted!'})
