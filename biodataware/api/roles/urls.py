from django.conf.urls import url
from .views import RoleList, RoleDetail, PIList, PIDetail


# only for admin
urlpatterns = [
    # all role list, post
    url(r'^$', RoleList.as_view(), name='roles'),
    # detail, delete
    url(r'^(?P<pk>[0-9]+)/$', RoleDetail.as_view(), name='role-detail'),
    # pi manager list
    url(r'^users/$', PIList.as_view(), name='pis'),
    # pi manager detail, post and delete
    url(r'^users/(?P<pk>[0-9]+)/$', PIDetail.as_view(), name='pi-detail')
]

app_name = 'api_roles'
