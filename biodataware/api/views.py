from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *


# user list
class UserList(APIView):
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetail(APIView):

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user).data
        return Response(serializer)

    # only allow to update self info
    def post(self, request, pk, format=None):
        pass
