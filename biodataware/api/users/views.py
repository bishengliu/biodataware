from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from datetime import datetime, timedelta
import pytz
from users.models import UserRole
from .serializers import *
from api.permissions import IsReadOnlyOwner, IsOwner, IsOwnOrReadOnly, IsPIofUser, IsPIAssistantofUser, IsPIAssistantofUserOrReadOnly
from django.contrib.auth import authenticate, login, logout


# user list
# readonly for all
class UserList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# get and post user info
class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwnOrReadOnly)

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        serializer = UserSerializer(user)

        return Response(serializer.data)

    @transaction.atomic
    def put(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        serializer = UserDetailUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # save data
        data = serializer.data
        try:
            # update user
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            if ('first_name' in data) or ('last_name' in data) or ('email' in data):
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
            if 'birth_date' in data:
                profile.birth_date = data['birth_date']
            if 'telephone' in data:
                profile.telephone = data['telephone']
            if request.FILES:
                if profile.photo:
                    profile.photo.delete()
                profile.photo = request.FILES['photo']
            if ('birth_date' in data) or ('telephone' in data) or request.FILES:
                profile.save()
            return Response(serializer.data)
        except:
            return Response({'detail': _('something went wrong, user info is not updated!')}, status=status.HTTP_400_BAD_REQUEST)


# only pi or assistant can manager researchers in the group
class UserRoleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIAssistantofUserOrReadOnly, )

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        roles = UserRole.objects.all().filter(user_id=pk)
        serializer = UserRoleSerializer(roles, many=True).data
        return Response(serializer)

    def post(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
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
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
        try:
            role = UserRole.objects.get(pk=ur_pk)
            serializer = UserRoleSerializer(role).data
            return Response(serializer)
        except:
            return Response({'detail': 'user role not found!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, ur_pk, format=None):
        user = get_object_or_404(User, pk=pk)
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
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
            if user.is_active is False:
                return Response({'detail': 'user is deactivated!'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                token, created = Token.objects.get_or_create(user=user)
                utc_now = datetime.utcnow()
                utc_now = utc_now.replace(tzinfo=pytz.UTC)
                if not created and token.created < utc_now - timedelta(hours=self.EXPIRE_HOURS):
                    token.delete()
                    token = Token.objects.create(user=user)
                    token.created = datetime.utcnow()
                    token.save()
                    return Response({'token': token.key, 'user': user.pk})
            except:
                return Response({'detail': 'fail to obtain token!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# owner only
# GET request to obtain token
class GetMyToken(APIView):
    permission_classes = (permissions.IsAuthenticated, IsReadOnlyOwner,)
    EXPIRE_HOURS = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS', 24)

    def get(self, request, format=None):
        user = request.user
        if user.is_active is False:
            return Response({'detail': 'user is deactivated!'}, status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(request, user)
        # get token
        try:
            token, created = Token.objects.get_or_create(user=user)  # create token
            utc_now = datetime.utcnow()
            utc_now = utc_now.replace(tzinfo=pytz.UTC)
            if not created and token.created < utc_now - timedelta(hours=self.EXPIRE_HOURS):
                token.delete()
                token = Token.objects.create(user=user)
                token.created = datetime.utcnow()
                token.save()
            return Response({'token': token.key, 'user': user.pk})
        except:
            return Response({'detail': 'fail to obtain token!'}, status=status.HTTP_400_BAD_REQUEST)


# owner only
# update my password
class UserPassword(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        user = request.user
        if user.is_active is False:
            return Response({'detail': 'user is deactivated!'}, status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(request, user)  # check the permission
        serializer = PasswordSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        # save new password
        try:
            data = serializer.data
            # check old_password
            if not user.check_password(data['old_password']):
                return Response({'detail': 'wrong password!'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data['new_password'])
            user.save()

            # new token
            token, created = Token.objects.get_or_create(user=user)  # create token
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.utcnow()
            token.save()

            return Response({'detail': 'Your password was successfully changed!'})
        except:
            return Response({'detail': 'something went wrong, password not changed!'}, status=status.HTTP_400_BAD_REQUEST)


# register new user
class Register(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        try:
            serializer = UserCreateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data

            username = data.get('username')
            email = data.get('email')
            first_name = data.get('first_name', "")
            last_name = data.get('last_name', "")
            user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            user.set_password(data.get('password1'))
            user.save()
            Token.objects.create(user=user)  # create token

            Profile.objects.create(
                user=user,
                birth_date=data.get('birth_date'),
                telephone=data.get('telephone'),
                photo=request.FILES['photo'] if request.FILES else None  # auto upload file
            )
            # login user
            user = authenticate(username=data['username'], password=data.get('password1'))
            if user is not None:
                if user.is_active:
                    login(request, user)

                    return Response({'detail': 'user created!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'user not created!'}, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    queryset = User.objects.all()

    def get(self, request, format=None):
        try:
            logout(request)
            #request.user.auth_token.delete()
            return Response({'detail': 'user logout!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'logout failed!'}, status=status.HTTP_400_BAD_REQUEST)