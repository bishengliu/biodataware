from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from datetime import datetime, timedelta
import pytz
from users.models import UserRole
from groups.models import Group
from .serializers import *
from api.permissions import IsReadOnlyOwner, IsOwner, IsOwnOrReadOnly, IsPIorAssistantofUser
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json

from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template import loader

# user list
# readonly for all
class UserList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# group count
class UserCount(APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get(self, request, format=None):
        user_count = User.objects.all().count()
        return Response({'count': user_count}, status=status.HTTP_200_OK)


# get and post user info
class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwnOrReadOnly)
    EXPIRE_HOURS = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS', 24)
    parser_classes = (JSONParser, FormParser, MultiPartParser,)

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

        serializer = UserDetailUpdateSerializer(data=obj, partial=True)
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
            if has_photo:
                if profile.photo:
                    profile.photo.delete()
                profile.photo = form_data['file'][0]
            if ('birth_date' in data) or ('telephone' in data) or has_photo:
                profile.save()

            # get the token
            token, created = Token.objects.get_or_create(user=user)  # create token
            utc_now = datetime.utcnow()
            utc_now = utc_now.replace(tzinfo=pytz.UTC)
            if not created and token.created < utc_now - timedelta(hours=self.EXPIRE_HOURS):
                token.delete()
                token = Token.objects.create(user=user)
                token.created = datetime.utcnow()
                token.save()
            return Response({'detail': True, 'token': token.key, 'user': user.pk}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': False}, status=status.HTTP_400_BAD_REQUEST)


# get user image
class UserImage(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission

        if user.profile is not None and user.profile.photo is not None:
            image = user.profile.photo
            # get image type
            image_type = image.name.split(".")[-1]
            content_type = "image/"+image_type+'"'
            return HttpResponse(image, content_type=content_type)
        return Response({'detail': 'image not found!'}, status=status.HTTP_400_BAD_REQUEST)


# search user info
# {'query': 'username', 'value': value}
class UserSearch(APIView):

    def post(self, request, format=None):
        key = request.data.get('query', '')
        value = request.data.get('value', '')
        user_pk = int(request.data.get('user_pk', -1))
        try:
            if key == 'username' and value:
                user = User.objects.all().filter(username__iexact=value).first()
                if user:
                    return Response({'matched': True, 'user': UserSerializer(user).data})
            if key == 'email' and value:
                if user_pk >= 0:
                    user = User.objects.all().exclude(pk=user_pk).filter(email__iexact=value).first()
                    if user:
                        return Response({'matched': True, 'user': UserSerializer(user).data})
                else:
                    user = User.objects.all().filter(email__iexact=value).first()
                    if user:
                        return Response({'matched': True, 'user': UserSerializer(user).data})
            return Response({'matched': False, 'user': ''})
        except:
            return Response({'detail': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)


# get auth user details
class AuthUserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


# only pi or assistant can manager researchers in the group
class UserRoleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUser, )

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        obj = {'user': user}
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
            role = get_object_or_404(Role, pk=data['role_id'])
            if role.role.lower() == "pi":
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
    permission_classes = (permissions.IsAuthenticated, IsPIorAssistantofUser,)

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
            if user_role.role.lower() == "pi":
                return Response({'detail': 'cannot remove role: ' + user_role.role + '!'},
                                status=status.HTTP_400_BAD_REQUEST)
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
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        if data['username'] and data['password']:
            user = User.objects.get(username=data['username'])
            if user is not None and user.check_password(data['password']):
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
        return Response("Something went wrong", status=status.HTTP_400_BAD_REQUEST)


# owner only
# GET request to obtain token
class GetMyToken(APIView):
    permission_classes = (permissions.IsAuthenticated, IsReadOnlyOwner,)
    EXPIRE_HOURS = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS', 24)

    def get(self, request, format=None):
        user = request.user
        if user.is_active is False:
            return Response({'detail': 'user is deactivated!'}, status=status.HTTP_400_BAD_REQUEST)
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)
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
        obj = {
            'user': user
        }
        self.check_object_permissions(request, obj)  # check the permission
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

            return Response({'detail': 'Your password was successfully changed!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'something went wrong, password not changed!'}, status=status.HTTP_400_BAD_REQUEST)


# register new user
class Register(APIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser, )
    @transaction.atomic
    def post(self, request, format=None):
        form_data = dict(request.data)
        # check upload photo
        has_photo = False
        if 'file' in form_data.keys():
            has_photo = True
        # form model data
        model = form_data['obj'][0]
        # load into dict
        obj = json.loads(model)
        profile = Profile()
        try:
            serializer = UserCreateSerializer(data=obj, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            username = data.get('username')
            email = data.get('email')
            first_name = data.get('first_name', "")
            last_name = data.get('last_name', "")
            user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            user.set_password(data.get('password1'))
            user.save()
            token = Token.objects.create(user=user)  # create token

            profile = Profile.objects.create(
                user=user,
                birth_date=data.get('birth_date', ''),
                telephone=data.get('telephone', ''),
                photo=form_data['file'][0] if has_photo else None  # auto upload file
            )
            profile.save()

            # auto create pi role
            group = Group.objects.all().filter(email__iexact=email).first()
            if group is not None:
                # check PI role
                pi_role = Role.objects.all().filter(role__exact='PI').first()
                if pi_role is not None:
                    auto_pi_role = UserRole.objects.create(
                        role_id=pi_role.pk,
                        user_id=user.pk)
                    auto_pi_role.save()

            # return user token
            return Response({'detail': True, 'token': token.key, 'user': user.pk}, status=status.HTTP_200_OK)
        except:
            if profile.photo is not None:
                profile.photo.delete()
            return Response({'detail': False}, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    queryset = User.objects.all()

    def get(self, request, format=None):
        try:
            logout(request)
            # request.user.auth_token.delete()
            return Response({'detail': 'user logout!'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'logout failed!'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):

    def post(self, request):
        try:
            obj = dict(request.data)
            serializer = ResetPasswordSerializer(data=obj.get('obj'))
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            # get email
            email = data.get('email', '')
            url = data.get('url', '')
            default_from_email = data.get('default_from_email', '')

            user = User.objects.get(email__iexact=email)
            if user is not None:
                c = {
                    'email': email,
                    'url': url,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                }
                email_template_name = 'users/api_password_reset_email.html'
                subject = 'Password reset on ' + url
                subject = ''.join(subject.splitlines())
                email = loader.render_to_string(email_template_name, c)
                send_mail(subject, email, default_from_email, [user.email], fail_silently=False)
                return Response({'detail': 'email has been sent!'}, status=status.HTTP_200_OK)
            return Response({'detail': 'not matched user!'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'reset password failed!'}, status=status.HTTP_400_BAD_REQUEST)


# confirm reset password
class ConfirmResetPassword(APIView):
    def post(self, request, uidb64=None, token=None):
        try:
            serializer = ConfirmResetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            assert uidb64 is not None and token is not None  # checked by URLconf
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                new_password = data.get('new_password1', '')
                user.set_password(new_password)
                user.save()
                # new token
                token, created = Token.objects.get_or_create(user=user)
                token.delete()
                Token.objects.create(user=user)  # create token
                return Response({'detail': 'password reset!'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'reset password failed!'}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({'detail': 'reset password failed!'}, status=status.HTTP_400_BAD_REQUEST)


