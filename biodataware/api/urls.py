from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view
from rest_framework.authtoken import views as rest_framework_views
from .views import UserList, UserDetail


urlpatterns = [

    #users
    url(r'^users/$', UserList.as_view(), name='users'),
    url(r'^users/(?P<pk>[0-9]+)/$', UserDetail.as_view(), name='user_detail'),


    # get token by posting { 'username': 'admin', 'password': 'admin' }
    url(r'^users/get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),



    # docs ui
    url(r'^docs/', get_swagger_view(title='API Docs')),
]
