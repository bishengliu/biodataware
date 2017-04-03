from django.conf.urls import url, include
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [

    # roles only by admin
    url(r'^roles/', include('api.roles.urls', namespace='api_roles')),
    # users
    url(r'^users/', include('api.users.urls', namespace='api_users')),
    # groups
    url(r'^groups/', include('api.groups.urls', namespace='api_groups')),
    # containers
    url(r'^containers/', include('api.containers.urls', namespace='api_containers')),
    # docs ui
    url(r'^docs/', get_swagger_view(title='API Docs')),
]
