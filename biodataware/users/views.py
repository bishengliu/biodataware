from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from .forms import RegistrationForm, LoginForm, UserForm, ProfileForm, PasswordForm
from .models import User, Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authtoken.models import Token


# register user
class RegisterView(View):
    form_class = RegistrationForm
    template_name = "users/users-register.html"

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    @transaction.atomic
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            # save user
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            Token.objects.create(user=user)  # create token

            Profile.objects.create(
                user=user,
                birth_date=form.cleaned_data['birth_date'],
                photo=request.FILES['photo'] if request.FILES else None   # auto upload file
            )
            # login user
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home:index')

        return render(request, self.template_name, {'form': form})


# login user
class LoginView(View):
    form_class = LoginForm
    template_name = "users/users-login.html"

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data.get('password')
            # authenticate
            user = authenticate(username=username, password=password)
            # check user
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home:index')
                else:
                    messages.add_message(request, messages.WARNING,
                                         _('User is disabled!'))
                    return redirect('login')
            else:
                messages.add_message(request, messages.WARNING, _('Login Failed, password was incorrect!'))
                return redirect('login')
        return render(request, self.template_name, {'form': form})


# logout user
class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('home:index')


# update user model and profile
class UpdateView(LoginRequiredMixin, View):
    template_name = "users/users-update.html"

    def get(self, request, *args, **kwargs):
        # get the user
        user = request.user
        # user form
        uf = UserForm(instance=user)
        # get the profile
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            # create profile if not exist
            profile = Profile.objects.create(
                user=user,
                photo=None  # auto upload file
            )
        # profile form
        upf = ProfileForm(instance=profile)
        photo_url = profile.photo.url if profile.photo else ''
        return render(request, self.template_name, {'uf': uf, 'upf': upf, 'photo': photo_url})

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # get the user
        user = request.user
        # forms
        uf = UserForm(request.POST)
        upf = ProfileForm(request.POST)

        if uf.is_valid() and upf.is_valid():
            # update user info
            user.first_name = uf.cleaned_data['first_name']
            user.last_name = uf.cleaned_data['last_name']
            user.email = uf.cleaned_data['email']
            user.save()
            # update profile
            profile = user.profile
            profile.birth_date = upf.cleaned_data['birth_date']
            profile.user = user
            if request.FILES:
                if profile.photo:
                    profile.photo.delete()
                profile.photo = request.FILES['photo']
            profile.save()
            messages.success(request, _('Your profile was successfully updated!'))

        # get user and profile
        profile = user.profile
        photo_url = profile.photo.url if profile.photo else ''  # photo url
        uf = UserForm(instance=user)
        upf = ProfileForm(instance=profile)
        return render(request, self.template_name, {'uf': uf, 'upf': upf, 'photo': photo_url})


# change password
class PasswordView(LoginRequiredMixin, View):
    template_name = "users/users-password.html"
    form_class = PasswordForm

    def get(self, request, *args, **kwargs):
        form = PasswordForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = PasswordForm(request.POST, user=request.user)

        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            #new token
            token, created = Token.objects.get_or_create(user=user)
            token.delete()
            Token.objects.create(user=user)  # create token
            messages.success(request, _('Your password was successfully changed!'))
            return redirect('home:index')
        else:
            return render(request, self.template_name, {'form': form})
