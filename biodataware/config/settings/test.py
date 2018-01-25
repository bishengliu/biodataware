"""
Test Configurations

"""
from .common import *

# some variables, must be all capitals
APP_NAME = 'BioDataWare'
APP_VERSION = '0.0.1'

# define app mode
APP_MODE = 'test'

# set this to allow use "if debug" in template
INTERNAL_IPS = (
    '0.0.0.0',
    '127.0.0.1',
)

# message level
MESSAGE_LEVEL = 10  # DEBUG


ALLOWED_HOSTS = ['*']

# message level
MESSAGE_LEVEL = 10  # DEBUG


# https://github.com/ottoyiu/django-cors-headers/#configuration
# cors rest api request
CORS_ORIGIN_ALLOW_ALL = True

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
DEFAULT_FROM_EMAIL = 'bishengliu36@gmail.com'
SERVER_EMAIL = 'bishengliu36@gmail.com'
EMAIL_HOST = 'bishengliu36@gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'azure_a0bed7402d312ae0c71db9d57a71c67c@azure.com'
EMAIL_HOST_PASSWORD = 'boL5MRQUCtbM1K8'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
'''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'bishengliu36@gmail.com'
SERVER_EMAIL = 'bishengliu36@gmail.com'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'azure_a0bed7402d312ae0c71db9d57a71c67c@azure.com'
EMAIL_HOST_PASSWORD = 'boL5MRQUCtbM1K8'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# SITE_NAME = 'bioku.nl'
# SITE_PROTOCOL = 'http'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # During development only


# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", },
        'NAME': 'bioku',
        'USER': 'bioku',
        'PASSWORD': 'bioku',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# for development
SITE_ID = 1
