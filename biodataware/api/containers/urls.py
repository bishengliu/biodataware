from django.conf.urls import url
from .views import *


urlpatterns = [
    # ===================================================container list for admin=======================================
    url(r'^$', ContainerList.as_view(), name='containers'),  # container-towers
    # ===================================================container count for admin======================================
    url(r'^count/$', ContainerCount.as_view(), name='containers-count'),  # container-count

    # find container info
    url(r'^search/$', ContainerSearch.as_view(), name='user_search'),
    # ====================================================container detail==============================================
    url(r'^(?P<pk>[0-9]+)/$', ContainerDetail.as_view(), name='container-detail'),

    # ======================================================group container list========================================
    url(r'^(?P<ct_id>[0-9]+)/groups/$', GroupContainerList.as_view(), name='groupcontainers'),

    # ====================================================group container detail========================================
    url(r'^(?P<ct_id>[0-9]+)/groups/(?P<gp_id>[0-9]+)/$', GroupContainerDetail.as_view(), name='groupcontainers-detail'),

    # ====================================================tower details=================================================
    # shelf list, number of shelves
    # containers/container_id/12-(tower_id)/ or containers/container_id/12(tower_id)/
    # list all the possible towers in the containers
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+(\-)*)/$',
        Tower.as_view(),
        name='container-tower-shelves'),


    # =======================================================shelf details==============================================
    # =======================================================box list===================================================
    # /12(tower_id)/3(shelf_id)/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/$',
        ShelfAlternative.as_view(),
        name='container-tower-shelf-boxes-alternative'),
    # /12-3-/ or /12-3/
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+(\-)*)/$',
        Shelf.as_view(),
        name='container-tower-shelf-boxes'),

    # quick get the box list
    # boxes in on container
    url(r'^(?P<ct_id>[0-9]+)/boxes/$',  ContainerBoxList.as_view(), name='container-boxes'),


    # =======================================================sample list================================================
    # add new sample
    # /12/3/4(box_id)/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/$',
        BoxAlternative.as_view(),
        name='container-tower-shelf-box-samples-alternative'),
    # /12-3-4(box)/
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/$',
        Box.as_view(),
        name='container-tower-shelf-box-samples'),

    # sample list
    # /boxes/12-3-4/
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/$',
        Box.as_view(),
        name='container-boxes-samples'),

    # update box rate
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/rate/$',
        BoxRate.as_view(),
        name='container-box-rate'),

    # update box color
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/color/$',
        BoxColor.as_view(),
        name='container-box-color'),

    # update box description
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/description/$',
        BoxDescription.as_view(),
        name='container-box-description'),

    # =====================================================sample detail================================================
    # edit sample
    # /12/3/4/A12/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/$',
        SampleDetailAlternative.as_view(),
        name='container-tower-shelf-box-sample-detail'),
    # 12-3-4/A12/
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/$',
        SampleDetail.as_view(),
        name='container-tower-shelf-box-sample-detail'),
    # 12-3-4/A12/update/
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/update/$',
        SampleDetailUpdate.as_view(),
        name='container-tower-shelf-box-sample-detail-update'),
    # 12-3-4/A12/switch_position/
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/switch_position/$',
        SampleSwitchPosition.as_view(),
        name='container-tower-shelf-box-sample-switch-position'),

    # /boxes/12-3-4/A12/
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/$',
        SampleDetail.as_view(),
        name='container-boxes-sample-detail'),


    # =============================================sample attachments list==============================================
    # /12/3/4/A12/attachments/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/attachments/$',
        SampleAttachmentListAlternative.as_view(),
        name='container-tower-shelf-box-sample-attachments'),
    # /12-3-4/A12/attachments/
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/attachments/$',
        SampleAttachmentList.as_view(),
        name='container-tower-shelf-box-sample-attachments'),

    # /boxes/12-3-4/A12/attachments/
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/attachments/$',
        SampleAttachmentList.as_view(),
        name='container-boxes-sample-attachments'),

    # =====================================================sample attachment details====================================
    # /12/3/4/A12/attachments/
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/attachments/(?P<at_id>[0-9]+)/$',
        SampleAttachmentDetailAlternative.as_view(),
        name='container-tower-shelf-box-sample-attachments-detail'),
    # /12-3-4/A12/attachments/
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/attachments/(?P<at_id>[0-9]+)/$',
        SampleAttachmentDetail.as_view(),
        name='container-tower-shelf-box-sample-attachments-detail'),

    # /boxes/12-3-4/A12/attachments/
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/attachments/(?P<at_id>[0-9]+)/$',
        SampleAttachmentDetail.as_view(),
        name='container-boxes-sample-attachments-detail'),


    # ==============================================take sample out=====================================================
    # /12/3/4/A12/take
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/take/$',
        SampleTakeAlternative.as_view(),
        name='container-tower-shelf-box-sample-out'),
    # 12-3-4/A12/take
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/take/$',
        SampleTake.as_view(),
        name='container-tower-shelf-box-sample-out'),

    # /boxes/12-3-4/A12/take
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/take/$',
        SampleTake.as_view(),
        name='container-boxes-sample-out'),

    # =================================================put sample back==================================================
    # /12/3/4/A12/back
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/back/$',
        SampleBackAlternative.as_view(),
        name='container-tower-shelf-box-sample-back'),
    # 12-3-4/A12/back
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/back/$',
        SampleBack.as_view(),
        name='container-tower-shelf-box-sample-back'),

    # /boxes/12-3-4/A12/back
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/back/$',
        SampleBack.as_view(),
        name='container-boxes-sample-back'),

    # ==================================================update sample color============================================
    # /12/3/4/A12/color
    url(r'^(?P<ct_id>[0-9]+)/(?P<tw_id>[0-9]+)/(?P<sf_id>[0-9]+)/(?P<bx_id>[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/color/$',
        SampleColorAlternative.as_view(),
        name='container-tower-shelf-box-sample-color'),
    # 12-3-4/A12/color
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/color/$',
        SampleColor.as_view(),
        name='container-tower-shelf-box-sample-color'),

    # /boxes/12-3-4/A12/color
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/color/$',
        SampleColor.as_view(),
        name='container-boxes-sample-color'),
]
