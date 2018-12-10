from django.conf.urls import url
from .views import *

urlpatterns = [
    # ===================================================container list for admin=======================================
    url(r'^$', ContainerList.as_view(), name='containers'),  # container-towers

    # move boxes
    url(r'^move_box/$', MoveBox.as_view(), name='container-move_boxes'),

    # swtich samples between 2 boxes
    url(r'^switch_samples/$', SwitchSample.as_view(), name='container-switch-samples'),

    # ===================================================container count for admin======================================
    url(r'^count/$', ContainerCount.as_view(), name='containers-count'),  # container-count

    # find container info
    url(r'^search/$', ContainerSearch.as_view(), name='user_search'),

    # search samples
    url(r'^search_samples/$', SearchSamples.as_view(), name='search_samples'),

    # pre search samples to return sample count
    url(r'^presearch_samples/$', PreSearchSamples.as_view(), name='presearch_samples'),

    # sample tags
    url(r'^tags/$', Tags.as_view(), name='sample_tags'),

    # remove sample attachment
    url(r'^samples/(?P<sp_id>[0-9]+)/(?P<at_id>[0-9]+)/$', DeleteAttachment.as_view(), name='remove-sample-attachment'),

    # upload attachment to sample
    url(r'^samples/(?P<sp_id>[0-9]+)/upload_attachment/$', UploadAttachment.as_view(), name='sample-upload_attachment'),

    # ====================================================container detail==============================================
    url(r'^(?P<pk>[0-9]+)/$', ContainerDetail.as_view(), name='container-detail'),

    # ====================================================add a box a container=========================================
    url(r'^(?P<pk>[0-9]+)/add_box/$', AddBox.as_view(), name='container-add-box'),

    # ======================================================group container list========================================
    url(r'^(?P<ct_id>[0-9]+)/groups/$', GroupContainerList.as_view(), name='groupcontainers'),

    # ====================================================group container detail========================================
    url(r'^(?P<ct_id>[0-9]+)/groups/(?P<gp_id>[0-9]+)/$', GroupContainerDetail.as_view(), name='groupcontainers-detail'),

    # =========================================upload samples to a freezer =============================================
    url(r'^(?P<pk>[0-9]+)/upload_samples/$', ContainerSampleUpload.as_view(), name='container-sample-upload'),

    # ====================================================tower details=================================================
    # shelf list, number of shelves
    # containers/container_id/12-(tower_id)/ or containers/container_id/12(tower_id)/
    # list all the possible towers in the containers
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+(\-)*)/$', Tower.as_view(), name='container-tower-shelves'),


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
    # group boxes in on container
    url(r'^(?P<ct_id>[0-9]+)/boxes/$',  ContainerBoxList.as_view(), name='container-boxes'),
    # get my group all the favorite boxes
    url(r'^(?P<ct_id>[0-9]+)/favorite_boxes/$',  ContainerFavoriteBoxList.as_view(), name='container-boxes'),
    # all the boxes in a container, including boxes of other groups
    url(r'^(?P<ct_id>[0-9]+)/all_boxes/$',  ContainerAllBoxList.as_view(), name='container-all_boxes'),

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

    # update box label
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/label/$',
        BoxLabel.as_view(),
        name='container-box-label'),

    # update box dimension
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/dimension/$',
        BoxDimension.as_view(),
        name='container-box-dimension'),

    # update box owner
    url(r'^(?P<ct_id>[0-9]+)/(?P<id>[0-9]+\-[0-9]+\-[0-9]+)/owner/$',
        BoxOwner.as_view(),
        name='container-box-owner'),

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
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/update_position/$',
        UpdateSamplePosition.as_view(),
        name='container-tower-shelf-box-sample-update-position'),
    # 12-3-4/switch_positions/
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/switch_positions/$',
        SampleSwitchPosition.as_view(),
        name='container-tower-shelf-box-sample-switch-positions'),

    # /boxes/12-3-4/A12/
    url(r'^(?P<ct_id>[0-9]+)/boxes/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/$',
        SampleDetail.as_view(),
        name='container-boxes-sample-detail'),
    # csample only
    # update csample parent level attr data
    # update one by one
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/(?P<sp_pk>[0-9]+)/(?P<at_id>[0-9]+)/update/$',
            UpdateCSampleData.as_view(),
            name='update-csampledata'),
    # update csamplesubdata one by one
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/(?P<sp_pk>[0-9]+)/subdata/$',
            UpdateCSampleSubData.as_view(),
            name='csamplesubdata'),
    url(r'^(?P<ct_id>[0-9]+)/(?P<bx_id>[0-9]+\-[0-9]+\-[0-9]+)/(?P<sp_id>[a-zA-Z][0-9]+)/(?P<sp_pk>[0-9]+)/delete_subdata/$',
            DeleteCSampleSubData.as_view(),
            name='delete_csamplesubdata'),
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
