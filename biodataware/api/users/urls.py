from django.conf.urls import url
from .views import UserList, UserDetail, GetMyToken, ObtainToken, UserPassword, UserRoleDetail, UserRoleDelete


urlpatterns = [

    # all users list
    url(r'^$', UserList.as_view(), name='users'),

    # get or post user details
    url(r'^(?P<pk>[0-9]+)/$', UserDetail.as_view(), name='user_detail'),

    # list all user roles or add user role
    url(r'^(?P<pk>[0-9]+)/role/$', UserRoleDetail.as_view(), name='user_role'),

    # remove user role
    url(r'^(?P<pk>[0-9]+)/role/(?P<ur_pk>[0-9]+)/$', UserRoleDelete.as_view(), name='user_role_remove'),

    # post to change password
    url(r'^password/$', UserPassword.as_view(), name='my_password'),
    # get token for testing purpose
    url(r'^token/$', GetMyToken.as_view(), name='my_token'),

    # get token by posting { 'username': 'admin', 'password': 'admin' }
    url(r'^token/$', ObtainToken.as_view(), name='user_token'),
]
