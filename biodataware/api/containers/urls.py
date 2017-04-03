from django.conf.urls import url
from .views import  *


urlpatterns = [
    # all container list
    url(r'^$', ContainerList.as_view(), name='containers'),
   # container detail
    url(r'^(?P<pk>[0-9]+)/$', ContainerDetail.as_view(), name='container-detail'),
]