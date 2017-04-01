from django.conf.urls import url, include
from rest_framework_swagger.views import get_swagger_view

'''
    # users list
    url(r'^users/$', UserList.as_view(), name='users'),

    # get or post user infor
    url(r'^users/(?P<pk>[0-9]+)/$', UserDetail.as_view(), name='user_detail'),

    # post to change password
    url(r'^users/password/$', UserPassword.as_view(), name='user_password'),
    # get token for testing purpose
    url(r'^users/token/$', GetMyToken.as_view(), name='my_token'),

    # get token by posting { 'username': 'admin', 'password': 'admin' }
    url(r'^users/token/$', ObtainToken.as_view(), name='token'),

'''
urlpatterns = [

    # roles only by admin
    url(r'^roles/', include('api.roles.urls', namespace='api_roles')),
    # users
    url(r'^users/', include('api.users.urls', namespace='api_users')),
    # groups
    url(r'^groups/', include('api.groups.urls', namespace='api_groups')),
    # docs ui
    url(r'^docs/', get_swagger_view(title='API Docs')),
]
