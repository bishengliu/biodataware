from django.conf.urls import url
from .views import *

urlpatterns = [
    # ctypes list and new ctype
    url(r'^$', CTypeList.as_view(), name='ctype-list'),
    # validate type name validate_name
    url(r'^validate_name/$', CTypeValidation.as_view(), name='ctype-validation'),
    # get minial attrs for any types
    url(r'^(?P<pk>[0-9]+)/$', CTypeDetail.as_view(), name='ctype-detail'),
    url(r'^(?P<pk>[0-9]+)/attrs/$', CTypeAttrList.as_view(), name='ctype-attrs'),
    # validate attr name
    url(r'^(?P<pk>[0-9]+)/validate_attr_name/$', CTypeAttrValidation.as_view(), name='ctype-attr-validation'),
    url(r'^(?P<pk>[0-9]+)/attrs/(?P<attr_pk>[0-9]+)/$', CTypeAttrDetail.as_view(), name='ctype-attr-detail'),
    # validate subattrs
    url(r'^(?P<pk>[0-9]+)/attrs/(?P<attr_pk>[0-9]+)/validate_subattr_name/$', CTypeSubAttrValidation.as_view(), name='ctype-subattr-Validation'),
    url(r'^(?P<pk>[0-9]+)/attrs/(?P<attr_pk>[0-9]+)/subattrs/$', CTypeSubAttrList.as_view(), name='ctype-attr-subattrs'),
    url(r'^(?P<pk>[0-9]+)/attrs/(?P<attr_pk>[0-9]+)/subattrs/(?P<subattr_pk>[0-9]+)/$', CTypeSubAttrDetail.as_view(), name='ctype-attr-subattr-detail'),
]


app_name = 'api_ctypes'
