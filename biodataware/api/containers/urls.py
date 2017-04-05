from django.conf.urls import url
from .views import *


urlpatterns = [
    # all container list
    url(r'^$', ContainerList.as_view(), name='containers'),  # container-towers
    # container detail
    url(r'^(?P<pk>[0-9]+)/$', ContainerDetail.as_view(), name='container-detail'),
    # group container list view
    url(r'^(?P<ct_id>[0-9]+)/groups/$', GroupContainerList.as_view(), name='groupcontainers'),
    # group container detail view
    url(r'^(?P<ct_id>[0-9]+)/groups/(?P<pk>[0-9]+)/$', GroupContainerDetail.as_view(), name='groupcontainers-detail'),


    # tower details
    # shelf list, number of shelves
    # /12-/ or /12/
    # list all the possible towers in the containers
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+(\-)*)/$',
        Tower.as_view(),
        name='container-tower-shelves'),

    # shelf details
    # box list
    # /12/3/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/$',
        ShelfAlternative.as_view(),
        name='container-tower-shelf-boxes'),
    # /12-3-/ or /12-3/
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+(\-)*)/$',
        Shelf.as_view(),
        name='container-tower-shelf-boxes'),

    # quick get the box list
    # boxes in on container
    url(r'^(?P<ct_id>[0-9]+)/boxes/$',
        ContainerBoxList.as_view(),
        name='container-boxes'),

    # sample list
    # /12/3/4/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/$',
        BoxAlternative.as_view(),
        name='container-tower-shelf-box-samples'),
    # /12-3-4/
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/$',
        Box.as_view(),
        name='container-tower-shelf-box-samples'),

    # sample list in the box
    # /boxes/12-3-4/
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/$',
        Box.as_view(),
        name='container-boxes-samples'),

#  ==========================================================================================================
    # sample detail in the box
    # /12/3/4/A12/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<pk>[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/$',
        SampleDetailAlternative.as_view(),
        name='container-tower-shelf-box-sample-detail'),
    # 12-3-4/A12/
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/$',
        SampleDetail.as_view(),
        name='container-tower-shelf-box-sample-detail'),


    # sample detail
    # /boxes/12-3-4/A12/
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/$',
        SampleDetail.as_view(),
        name='container-boxes-sample-detail'),


]