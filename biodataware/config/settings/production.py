"""
Production Configurations

"""

from .common import *

# some variables, must be all capitals
APP_NAME = 'BioDataWare'
APP_VERSION = '2.0.0'

# define app mode
APP_MODE = 'production'

DEBUG = False


ALLOWED_HOSTS = ['*']

# message level
MESSAGE_LEVEL = 10  # DEBUG

STATIC_ROOT = os.path.join(APPS_DIR, 'static')

# need to change this to restrict the access to the backend
# https://github.com/ottoyiu/django-cors-headers/#configuration
# cors rest api request
# CORS_ORIGIN_WHITELIST = (
#     'http://localhost'
# )
# allow all for access
CORS_ORIGIN_ALLOW_ALL = True

# restful
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #    'rest_framework.permissions.IsAuthenticated',
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication', # token
        # 'helpers.authentication.ExpiringTokenAuthentication', # custom token
        'rest_framework.authentication.BasicAuthentication', # login plain password
        # 'rest_framework.authentication.SessionAuthentication', # session on the same server
    )
}

SITE_NAME = 'BIOKU'

# sendgrid
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'bliu@lumc.nl'
SERVER_EMAIL = 'bliu@lumc.nl'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'bisheng'
EMAIL_HOST_PASSWORD = 'Lbs198236'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

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
