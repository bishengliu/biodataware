from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .permissions import IsOwnOrReadOnly, IsReadOnlyOwner, IsOwner
from datetime import datetime, timedelta
import pytz
