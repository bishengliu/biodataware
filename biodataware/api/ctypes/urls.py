from django.conf.urls import url
from .views import *

urlpatterns = [
    # ctypes list and new ctype
    url(r'^$', CTypeList.as_view(), name='containers'),

]
