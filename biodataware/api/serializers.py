from rest_framework import serializers
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
import re
from helpers.validators import validate_phone
from users.models import User, UserRole, Profile
from roles.models import Role
from groups.models import Group, Assistant, GroupResearcher
from containers.models import Container, GroupContainer, BoxContainer, BoxResearcher
from samples.models import Biosystem, Tissue, Sample, SampleAttachment, SampleTissue, SampleResearcher
