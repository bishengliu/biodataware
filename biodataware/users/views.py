from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from .forms import RegistrationForm, LoginForm, UserForm, ProfileForm, PasswordForm, ResetPassword, NewPassword
from .models import User, Profile
from groups.models import Group, GroupResearcher
from users.models import UserRole, Role
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authtoken.models import Token
from django.conf import settings

from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template import loader


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
            try:
                # save user
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                user = User(username=username, email=email, first_name=first_name, last_name=last_name)
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                Token.objects.create(user=user)  # create token

                profile = Profile.objects.create(
                    user=user,
                    birth_date=form.cleaned_data['birth_date'],
                    photo=request.FILES['photo'] if request.FILES else None  # auto upload file
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
                        # auto add user to the group
                        groupresearcher = GroupResearcher.objects.create(
                            user_id=user.pk,
                            group_id=group.pk
                        )
                        groupresearcher.save()

                # login user
                user = authenticate(username=username, password=form.cleaned_data.get('password1'))
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('home:index')
            except:
                messages.success(request, _('Something went wrong! Please try again later!'))
                return redirect('register')
        messages.success(request, _('Something went wrong! Please fill the correctly!'))
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
            try:
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
            except:
                messages.add_message(request, messages.WARNING, _('Login Failed, please try again!'))
                return redirect('login')
        messages.add_message(request, messages.WARNING, _('Login Failed, please try again!'))
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
        try:
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
        except:
            messages.success(request, _('Something went wrong! Your profile was not updated!'))
            return redirect('users:update')


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
            try:
                user = request.user
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                # new token
                token, created = Token.objects.get_or_create(user=user)
                token.delete()
                Token.objects.create(user=user)  # create token
                messages.success(request, _('Your password was successfully changed!'))
                return redirect('home:index')
            except:
                messages.success(request, _('Something went wrong, please try again!'))
                return redirect('home:index')
        else:
            messages.success(request, _('Something went wrong, please fill all the required fields!'))
            return render(request, self.template_name, {'form': form})


# forget password
class ResetPasswordView(View):
    form_class = ResetPassword
    template_name = "users/users-reset_password.html"

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                email = form.cleaned_data["email"]
                # find the user
                user = User.objects.get(email__iexact=email)
                if user is not None:
                    c = {
                        'email': email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': settings.SITE_NAME,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': settings.SITE_PROTOCOL,
                    }
                    email_template_name = 'users/password_reset_email.html'
                    subject = 'Password reset on ' + 'localhost'
                    # Email subject *must not* contain newlines
                    subject = ''.join(subject.splitlines())
                    email = loader.render_to_string(email_template_name, c)
                    messages.success(request,
                                     _(
                                         'Email has been sent to ' + email + "'s email address. Please check its inbox to continue reseting password."))
                    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    return redirect('login')
            except:
                messages.error(request, _('Something went wrong, please try again!'))
                return redirect('reset')
        messages.error(request, _('Something went wrong, please try again!'))
        return render(request, self.template_name, {'form': form})


# reset new password
class ResetPasswordConfirmView(View):

    form_class = NewPassword
    template_name = "users/users-reset_password_confirm.html"

    def get(self, request, uidb64=None, token=None, *arg, **kwargs):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            assert uidb64 is not None and token is not None  # checked by URLconf
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
                if user is not None and default_token_generator.check_token(user, token):
                    new_password = form.cleaned_data['password1']
                    user.set_password(new_password)
                    user.save()
                    # new token
                    token, created = Token.objects.get_or_create(user=user)
                    token.delete()
                    Token.objects.create(user=user)  # create token
                    messages.success(request, _('Password has been reset. Please login with the new password!'))
                    return redirect('login')
                else:
                    messages.error(request, _('The reset password link is no longer valid.'))
                    return self.form_invalid(form)
            except:
                messages.error(request, _('Password reset failed, please try again.'))
                return self.form_invalid(form)
        else:
            messages.error(request, _('Password reset failed, please try again.'))
            return self.form_invalid(form)