from django.shortcuts import render
from rest_framework import serializers, viewsets
from .serializers import *


# Create your views here.
class UserListView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
