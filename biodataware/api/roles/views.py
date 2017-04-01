from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from .serializers import *


from roles.models import Role
from users.models import UserRole


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
            role = Role(role=data['role'], description=data['description'])
            role.save()
            return Response({'detail': 'role added!'})
        except:
            return Response({'detail': 'role not added!'}, status=status.HTTP_400_BAD_REQUEST)


# role detail
class RoleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self,request, pk, format=None):
        role = get_object_or_404(Role, pk)
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        try:
            role = Role.objects.get(pk=pk)
            # check whether there are users with role
            researchers = UserRole.objects.all().filter(role_id=role.pk)
            if not researchers:
                role.delete()
                return Response({'detail': 'role is deleted!'})
            return Response({'detail': 'there are researchers with the current role, role can not be deleted!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'role is not deleted!'}, status=status.HTTP_400_BAD_REQUEST)