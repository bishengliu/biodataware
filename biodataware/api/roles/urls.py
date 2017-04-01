from django.conf.urls import url
from .views import RoleList, RoleDetail


urlpatterns = [
    # all role list, post
    url(r'^$', RoleList.as_view(), name='roles'),
    # detail, delete
    url(r'^(?P<pk>[0-9]+)/$', RoleDetail.as_view(), name='role-detail'),
]