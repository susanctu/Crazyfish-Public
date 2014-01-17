"""Development settings and globals."""


from common import *
import dj_database_url

########## DEBUG CONFIGURATION
DEBUG = False
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION

# Parse database configuration from $DATABASE_URL
DATABASES = dict()
DATABASES['default'] = dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']