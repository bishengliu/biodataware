from django.conf.urls import url
from .views import UserList, UserCount, UserDetail, GetMyToken, ObtainToken, UserPassword, UserRoleDetail, UserRoleDelete, Register, Logout, AuthUserDetail, UserImage, UserSearch, ResetPassword, ConfirmResetPassword


urlpatterns = [

    # all users list
    url(r'^$', UserList.as_view(), name='users'),
    url(r'^count/$', UserCount.as_view(), name='user-count'), #et group count
    # get or post user details
    url(r'^(?P<pk>[0-9]+)/$', UserDetail.as_view(), name='user_detail'),

    url(r'^(?P<pk>[0-9]+)/image/$', UserImage.as_view(), name='user_image'),

    # find user info
    url(r'^search/$', UserSearch.as_view(), name='user_search'),

    # get auth user details
    url(r'^auth_user/$', AuthUserDetail.as_view(), name='auth_user_detail'),

    # list all user roles or add user role
    url(r'^(?P<pk>[0-9]+)/role/$', UserRoleDetail.as_view(), name='user_role'),

    # remove user role
    url(r'^(?P<pk>[0-9]+)/role/(?P<ur_pk>[0-9]+)/$', UserRoleDelete.as_view(), name='user_role_remove'),

    # post to change password
    url(r'^password/$', UserPassword.as_view(), name='my_password'),
    # get token for testing purpose
    # url(r'^token/$', GetMyToken.as_view(), name='my_token'),

    # get token by posting { 'username': 'admin', 'password': 'admin' }
    url(r'^token/$', ObtainToken.as_view(), name='user_token'),

    # register
    url(r'^register/$', Register.as_view(), name='register'),

    # logout
    url(r'^logout/$', Logout.as_view(), name='logout'),

    # request reset password
    url(r'^reset_password/$', ResetPassword.as_view(), name='api-reset-password'),

    # request reset password confirm
    url(r'^reset_password_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ConfirmResetPassword.as_view(),
        name='api_reset_password_confirm'
        ),
]
