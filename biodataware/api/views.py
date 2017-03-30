from rest_framework import viewsets
from rest_framework.views import APIView
#from rest_framework.permissions import IsAuthenticated
from .serializers import *


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    #permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
