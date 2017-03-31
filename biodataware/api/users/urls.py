from django.conf.urls import url
from .views import UserList, UserDetail, GetMyToken, ObtainToken, UserPassword


urlpatterns = [

    # users list
    url(r'^$', UserList.as_view(), name='users'),

    # get or post user info
    url(r'^(?P<pk>[0-9]+)/$', UserDetail.as_view(), name='user_detail'),

    # post to change password
    url(r'^password/$', UserPassword.as_view(), name='user_password'),
    # get token for testing purpose
    url(r'^token/$', GetMyToken.as_view(), name='my_token'),

    # get token by posting { 'username': 'admin', 'password': 'admin' }
    url(r'^token/$', ObtainToken.as_view(), name='token'),
]
