from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .permissions import IsOwnOrReadOnly
from rest_framework.parsers import JSONParser


# user list
class UserList(APIView):
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetail(APIView):
    permission_classes = (IsOwnOrReadOnly,)

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user).data
        self.check_object_permissions(request, user)  # check the permission
        return Response(serializer)

    def post(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)  # check the permission
        serializer = UserDetailSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # save data
        data = serializer.data
        # update user
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.save()
        # update profile
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            # create profile if not exist
            profile = Profile.objects.create(
                user=user,
                photo=None,  # auto upload file
                telephone=None
            )
        profile.birth_date = data['birth_date']
        profile.telephone = data['telephone']
        if request.FILES:
            if profile.photo:
                profile.photo.delete()
            profile.photo = request.FILES['photo']
        profile.save()
        return Response(serializer.data)
