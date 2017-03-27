"""
Local settings

- Run in Debug mode

"""
from .common import *

# some variables, must be all capitals
APPNAME = 'BioDataWare'
APPVERSION = '0.0.1'

# define app mode
APP_MODE = 'local'

# set this to allow use "if debug" in template
INTERNAL_IPS = (
    '0.0.0.0',
    '127.0.0.1',
)

# message level
MESSAGE_LEVEL = 10  # DEBUG


