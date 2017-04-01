from django.conf.urls import url
from .views import GroupList, GroupDetail

urlpatterns = [

    # all users list
    url(r'^$', GroupList.as_view(), name='groups'),
    # group detail
    url(r'^(?P<pk>[0-9]+)/$', GroupDetail.as_view(), name='group-detail'),
]