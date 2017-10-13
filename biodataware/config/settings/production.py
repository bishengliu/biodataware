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


# https://github.com/ottoyiu/django-cors-headers/#configuration
# cors rest api request
CORS_ORIGIN_WHITELIST = (
    'http://localhost'
)

# restful
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication', # token
        #'helpers.authentication.ExpiringTokenAuthentication', # custom token
        #'rest_framework.authentication.BasicAuthentication', # login plain password
        #'rest_framework.authentication.SessionAuthentication', # session on the same server
    )
}


'''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'test@gmail.com'
SERVER_EMAIL = 'test@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'test@gmail.com'
EMAIL_HOST_PASSWORD = 'test123##'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
'''

SITE_NAME = 'bioku.nl'
SITE_PROTOCOL = 'http'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # During development only


# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bioku_test',
        'USER': 'bioku',
        'PASSWORD': 'bioku',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# for development
SITE_ID = 1
