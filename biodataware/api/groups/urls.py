from django.conf.urls import url
from .views import GroupList, GroupDetail, GroupResearcherList, GroupResearcherDetail

urlpatterns = [

    # all users list
    url(r'^$', GroupList.as_view(), name='groups'),
    # group detail
    url(r'^(?P<pk>[0-9]+)/$', GroupDetail.as_view(), name='group-detail'),
    # group researchers
    url(r'^researchers/$', GroupResearcherList.as_view(), name='researcher-detail'),
    #  group researcher detail
    url(r'^researchers/(?P<pk>[0-9]+)/$', GroupResearcherDetail.as_view(), name='researcher-detail'),
]