"""
Local settings

- Run in Debug mode

"""
from .common import *

# some variables, must be all capitals
APP_NAME = 'BioDataWare'
APP_VERSION = '0.0.1'

# define app mode
APP_MODE = 'local'

# set this to allow use "if debug" in template
INTERNAL_IPS = (
    '0.0.0.0',
    '127.0.0.1',
)

# message level
MESSAGE_LEVEL = 10  # DEBUG


CORS_ORIGIN_ALLOW_ALL = True

# restful
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    #'DEFAULT_PERMISSION_CLASSES': [
    #    'rest_framework.permissions.IsAuthenticated',
    #],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication', # login plain password
        'rest_framework.authentication.TokenAuthentication',  # token
        #'helpers.authentication.ExpiringTokenAuthentication', # custom token
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    )
}

# email for forgot password


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
SITE_NAME = 'localhost'
SITE_PROTOCOL = 'http'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # During development only


# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", },
        'NAME': 'bioku_test',
        'USER': 'bioku',
        'PASSWORD': 'bioku',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}