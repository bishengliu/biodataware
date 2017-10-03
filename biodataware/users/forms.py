from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from .models import User, Profile
from django.utils.translation import ugettext_lazy as _
import re


# register form
class RegistrationForm(forms.Form):
    # fields
    username = forms.RegexField(
        regex=r'^\w+$',
        widget=forms.TextInput(attrs=dict(required=True, max_length=30),),
        label=_("Username"),
        error_message={'invalid': _("Username contains only letters, numbers and underscores.")})
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=30),),
        label=_("Email"))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False),),
        label=_("Password"))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False),),
        label=_("Password (again)"))
    first_name = forms.RegexField(
        regex=r'^\w+$',
        widget=forms.TextInput(attrs=dict(required=False, max_length=30), ),
        required=False,
        label=_("First Name"),
        error_message={'invalid': _("First Name contains only letters, numbers and underscores.")})
    last_name = forms.RegexField(
        regex=r'^\w+$',
        widget=forms.TextInput(attrs=dict(required=False, max_length=30), ),
        required=False,
        label=_("Last Name"),
        error_message={'invalid': _("Last Name contains only letters, numbers and underscores.")})
    birth_date = forms.DateField(
        required=False,
        input_formats=settings.DATE_INPUT_FORMATS,
        label=_("Birth Date"))
    photo = forms.ImageField(
        max_length=100,
        allow_empty_file=True,
        # help_text= _('Only allow for ".bmp", ".jpg", ".tiff" and ".png"!'),
        required=False,  # default True
        label=_("Photo"))

    # validation
    def clean_username(self):
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_('The username already exists. Please try another one.'))

    # validate email
    def clean_email(self):
        try:
            User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_('The email already taken. Please try another one.'))

    # validate password1/2
    def clean(self):
        super(RegistrationForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
                msg = "The two password fields did not match."
                self.add_error('password1', _(msg))
                self.add_error('password2', _(msg))
                raise forms.ValidationError(_(msg))

            password_pattern = re.compile("^(?=.*[A-Z])(?=.*[a-z].*[a-z])(?=.*[0-9].*[0-9]).{8,}$")
            # isValid = re.match(password_pattern, self.cleaned_data.get('password1'))
            if not password_pattern.search(self.cleaned_data.get('password1')):
                msg = "Password contains at least: " \
                      "1 uppercase letter, 2 lowercase letters, 2 digits and must be longer than 8 characters."
                self.add_error('password1', _(msg))
                # self.add_error('password2', _(msg))
                raise forms.ValidationError(_(msg))
        return self.cleaned_data


# login form
class LoginForm(forms.Form):
    username = forms.RegexField(
        regex=r'^\w+$',
        widget=forms.TextInput(attrs=dict(required=True, max_length=30), ),
        label=_("Username"))

    password = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False),),
        label=_("Password"))

    # validation
    def clean_username(self):
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
            return self.cleaned_data['username']
        except User.DoesNotExist:
            raise forms.ValidationError(_('The username does not exist!'))


# for updating forms
class UserForm(forms.ModelForm):
    # validation
    def clean_first_name(self):
        name_pattern = re.compile("^\w+$")
        is_valid = re.match(name_pattern, self.cleaned_data.get('first_name'))
        if not is_valid:
            msg = "First Name contains only letters, numbers and underscores."
            raise forms.ValidationError(_(msg))
        return self.cleaned_data['first_name']

    def clean_last_name(self):
        name_pattern = re.compile("^\w+$")
        is_valid = re.match(name_pattern, self.cleaned_data.get('last_name'))
        if not is_valid:
            msg = "Last Name contains only letters, numbers and underscores."
            raise forms.ValidationError(_(msg))
        return self.cleaned_data['last_name']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'email')


class ProfileForm(forms.ModelForm):

    birth_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['birth_date'].required = True

    class Meta:
        model = Profile
        fields = ('birth_date', 'photo')


# change password form
class PasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False), ),
        label=_("Current Password"))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False), ),
        label=_("New Password"))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False), ),
        label=_("New Password (again)"))

    # add user
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordForm, self).__init__(*args, **kwargs)

    # validation
    def clean_password(self):
        if self.user:
            username = self.user.username
            try:
                if not authenticate(username=username, password=self.cleaned_data['password']):
                    raise forms.ValidationError(_('Current password is incorrect!'))
            except:
                raise forms.ValidationError(_('Current password is incorrect!'))

        return self.cleaned_data['password']

    # validate password1/2
    def clean(self):
        super(PasswordForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
                msg = "The two password fields did not match."
                self.add_error('password1', _(msg))
                self.add_error('password2', _(msg))
                raise forms.ValidationError(_(msg))

            password_pattern = re.compile("^(?=.*[A-Z])(?=.*[a-z].*[a-z])(?=.*[0-9].*[0-9]).{8,}$")
            if not password_pattern.search(self.cleaned_data.get('password1')):
                msg = "Password contains at least: " \
                          "1 uppercase letter, 2 lowercase letters, 2 digits and must be longer than 8 characters."
                self.add_error('password1', _(msg))
                raise forms.ValidationError(_(msg))
        return self.cleaned_data


# forget password
class ResetPassword(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=30), ),
        label=_("Email"))

    # validate email
    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
            if user is not None:
                return self.cleaned_data['email']
            else:
                raise forms.ValidationError(_('The email not found. Please try another one.'))
        except:
            raise forms.ValidationError(_('The email not found. Please try another one.'))


# reset password
class NewPassword(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False), ),
        label=_("New Password"))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False), ),
        label=_("New Password (again)"))

    # validate password1/2
    def clean(self):
        super(NewPassword, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
                msg = "The two password fields did not match."
                self.add_error('password1', _(msg))
                self.add_error('password2', _(msg))
                raise forms.ValidationError(_(msg))

            password_pattern = re.compile("^(?=.*[A-Z])(?=.*[a-z].*[a-z])(?=.*[0-9].*[0-9]).{8,}$")
            if not password_pattern.search(self.cleaned_data.get('password1')):
                msg = "Password contains at least: " \
                      "1 uppercase letter, 2 lowercase letters, 2 digits and must be longer than 8 characters."
                self.add_error('password1', _(msg))
                raise forms.ValidationError(_(msg))
        return self.cleaned_data