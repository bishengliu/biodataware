from django.conf.urls import url
from .views import RoleList, RoleDetail, PIManagerList, PIManagerDetail


urlpatterns = [
    # all role list, post
    url(r'^$', RoleList.as_view(), name='roles'),
    # detail, delete
    url(r'^(?P<pk>[0-9]+)/$', RoleDetail.as_view(), name='role-detail'),
    # pi manager list
    url(r'^users/$', PIManagerList.as_view(), name='pis'),
    # pi manager detail, post and delete
    url(r'^users/(?P<pk>[0-9]+)/$', PIManagerDetail.as_view(), name='pi-detail')
]