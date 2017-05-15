from django.conf.urls import url
from .views import GroupList, GroupCount, GroupDetail, GroupResearcherList, GroupResearcherDetail, OneGroupResearcherList, OneGroupResearcherDetail, MyGroupList, OneGroupAssistantList, OneGroupAssistantDetail, MyGroupUpdate, GroupSearch

urlpatterns = [

    # all users list
    url(r'^$', GroupList.as_view(), name='groups'),
    url(r'^count/$', GroupCount.as_view(), name='group-count'), #et group count
    # group detail
    url(r'^(?P<pk>[0-9]+)/$', GroupDetail.as_view(), name='group-detail'),

    # find group info
    url(r'^search/$', GroupSearch.as_view(), name='user_search'),

    # PI update own group info
    url(r'^update/$', MyGroupUpdate.as_view(), name='my-groups-update'),


    # my groups + members + assistants
    url(r'^mygroups/$', MyGroupList.as_view(), name='my-groups-list'),

    # list the researchers in all my groups
    url(r'^researchers/$', GroupResearcherList.as_view(), name='groups-researcher-list'),
    #  researcher detail in all my groups
    url(r'^researchers/(?P<pk>[0-9]+)/$', GroupResearcherDetail.as_view(), name='groups-researcher-detail'),


    # manage researchers in one group
    # list researchers in one of my groups
    url(r'^(?P<pk>[0-9]+)/researchers/$', OneGroupResearcherList.as_view(), name='one-group-researcher-list'),
    # researcher detail in one group
    url(r'^(?P<g_id>[0-9]+)/researchers/(?P<u_id>[0-9]+)/$', OneGroupResearcherDetail.as_view(), name='one-group-researcher-detail'),


    # manage assistants in one group
    # list researchers in one of my groups
    url(r'^(?P<pk>[0-9]+)/assistants/$', OneGroupAssistantList.as_view(), name='one-group-assistant-list'),
    # researcher detail in one group
    url(r'^(?P<g_id>[0-9]+)/assistants/(?P<u_id>[0-9]+)/$', OneGroupAssistantDetail.as_view(), name='one-group-assistant-detail'),


]
