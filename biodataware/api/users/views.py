from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
import pytz
from users.models import UserRole
from .serializers import *
from api.permissions import IsReadOnlyOwner, IsOwner, IsOwnOrReadOnly, IsPIofUser, IsPIAssistantofUser


# user list
# only admin can acccess all the users
class UserList(APIView):
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# every logged in user
# get and post user info
class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        self.check_object_permissions(request, user)  # check the permission
        return Response(serializer.data)

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


# only admin pi or assistant can
# get ot post user role
# only admin can add pi or manager
class UserRoleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIofUser, IsPIAssistantofUser, permissions.IsAdminUser,)

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)  # check the permission
        roles = UserRole.objects.all().filter(user_id=pk)
        serializer = UserRoleSerializer(roles, many=True).data
        return Response(serializer)

    def post(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)  # check the permission

        serializer = UserRoleCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            # save new password
            data = serializer.data
            # is admin
            if request.user.is_superuser is False:
                # check whether the role is Manger or PI
                role = get_object_or_404(Role, pk=data['role_id'])
                if (role.role.lower() == "manager") or (role.role.lower() == "pi"):
                    return Response({'detail': 'cannot add role ' + role.role + '!'},
                                    status=status.HTTP_400_BAD_REQUEST)
            # admin, pi or assistant
            user_role = UserRole(**data)
            user_role.save()
            return Response(serializer.data)
        except:
            return Response({'detail': 'user role not added!'}, status=status.HTTP_400_BAD_REQUEST)


# only admin, pi or assistant can
# delete user role
# only admin can delete pi or manager
class UserRoleDelete(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIofUser, IsPIAssistantofUser, permissions.IsAdminUser,)

    def get(self, request, pk, ur_pk, format=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)  # check the permission
        try:
            role = UserRole.objects.get(pk=ur_pk)
            serializer = UserRoleSerializer(role).data
            return Response(serializer)
        except:
            return Response({'detail': 'user role not found!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, ur_pk, format=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)  # check the permission
        try:
            user_role = UserRole.objects.get(pk=ur_pk)
            if request.user.is_superuser is False:
                # check whether the role is Manger or PI
                if (user_role.role.lower() == "manager") or (user_role.role.lower() == "pi"):
                    return Response({'detail': 'cannot remove role: ' + user_role.role + '!'},
                                    status=status.HTTP_400_BAD_REQUEST)
            # admin, pi or assistant
            user_role.delete()
            return Response({'detail': 'user role deleted!'})
        except:
            return Response({'detail': 'user role not deleted!'}, status=status.HTTP_400_BAD_REQUEST)


# owner only
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
                return Response({'token': token.key, 'user': user.username})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# owner only
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
        return Response({'token': token.key, 'user': user.username})


# owner only
# update my password
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
