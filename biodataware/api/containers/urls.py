from django.conf.urls import url
from .views import *


urlpatterns = [
    # all container list
    url(r'^$', ContainerList.as_view(), name='containers'),
    # container detail
    url(r'^(?P<pk>[0-9]+)/$', ContainerDetail.as_view(), name='container-detail'),
    # group container list view
    url(r'^(?P<ct_id>[0-9]+)/groups/$', GroupContainerList.as_view(), name='groupcontainers'),
    # group container detail view
    url(r'^(?P<ct_id>[0-9]+)/groups/(?P<pk>[0-9]+)/$', GroupContainerDetail.as_view(), name='groupcontainers-detail'),
    # assign container to a group, post only
    #url(r'^(?P<pk>[0-9]+)/add2group/$', ContainerDetail.as_view(), name='container-add2group'),
    # view and remove container from the group
]