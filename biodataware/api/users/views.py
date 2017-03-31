from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from api.permissions import IsReadOnlyOwner, IsOwner
from datetime import datetime, timedelta
import pytz


# user list
class UserList(APIView):
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# get and post user info
class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsReadOnlyOwner,)

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


# update password
class UserPassword(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def post(self, request, *args, **kwargs):
        user = request.user
        self.check_object_permissions(request, user)  # check the permission
        serializer = PasswordSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        # save new password
        data = serializer.data
        user.set_password(data['new_password'])
        user.save()

        # new token
        token, created = Token.objects.get_or_create(user=user)
        token.delete()
        Token.objects.create(user=user)
        return Response({'detail': _('Your password was successfully changed!')})


# POST request to get token, used for client side login/authentication
# create new token when expired
class ObtainToken(ObtainAuthToken):
    EXPIRE_HOURS = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS', 24)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid(raise_exception=True):
            user = serializer.object['user']
            token, created = Token.objects.get_or_create(user=user)
            utc_now = datetime.utcnow()
            utc_now = utc_now.replace(tzinfo=pytz.UTC)
            if not created and token.created < utc_now - timedelta(hours=self.EXPIRE_HOURS):
                token.delete()
                token = Token.objects.create(user=user)
                token.created = datetime.utcnow()
                token.save()
                return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET request to obtain token
class GetMyToken(APIView):
    permission_classes = (permissions.IsAuthenticated, IsReadOnlyOwner,)
    EXPIRE_HOURS = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS', 24)

    def get(self, request, format=None):
        user = request.user
        self.check_object_permissions(request, user)
        # get token
        token, created = Token.objects.get_or_create(user=user)  # create token
        utc_now = datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.UTC)
        if not created and token.created < utc_now - timedelta(hours=self.EXPIRE_HOURS):
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.utcnow()
            token.save()
        return Response({'token': token.key})
