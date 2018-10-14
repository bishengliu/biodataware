from django.conf.urls import url
from .views import *

urlpatterns = [
    # ctypes list and new ctype
    url(r'^$', CTypeList.as_view(), name='ctype-list'),
    url(r'^(?P<pk>[0-9]+)$', CTypeDetail.as_view(), name='ctype-detail'),
]
