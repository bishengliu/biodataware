"""
Production Configurations

"""

from .common import *

# some variables, must be all capitals
APP_NAME = 'BioDataWare'
APP_VERSION = '0.0.1'

# define app mode
APP_MODE = 'production'

DEBUG = False


ALLOWED_HOSTS = ['*']

# message level
MESSAGE_LEVEL = 10  # DEBUG


# restful
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication', # token
        'rest_framework.authentication.BasicAuthentication', # login plain password
        'rest_framework.authentication.SessionAuthentication', # session on the same server
    )
}
