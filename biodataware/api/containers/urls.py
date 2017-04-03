from django.conf.urls import url
from .views import  *


urlpatterns = [
    # all container list
    url(r'^$', ContainerList.as_view(), name='containers'),
]