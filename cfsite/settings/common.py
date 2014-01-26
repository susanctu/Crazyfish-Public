"""
Django common settings and globals for cfsite project.

"""

import sys
from os.path import abspath, basename, dirname, join, normpath

########## PATH CONFIGURATION
# Absolute filesystem path to this Django project directory.
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Site name.
SITE_NAME = basename(DJANGO_ROOT)

# Absolute filesystem path to the top-level project folder.
SITE_ROOT = dirname(DJANGO_ROOT)

# Project's SECRET_KEY
SECRET_KEY = 'hi+cioy%rx^zx_s)!fm#$*#1)c_c3gfk7l^zc06#yq6ze*xt-o'

# Add all necessary filesystem paths to our system path so that we can use
# python import statements.
sys.path.append(SITE_ROOT)
sys.path.append(normpath(join(DJANGO_ROOT, 'apps')))
sys.path.append(normpath(join(DJANGO_ROOT, 'libs')))
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# Disable debugging by default.
DEBUG = False
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# Admin and managers for this project. These people receive private site
# alerts.
ADMINS = (
    ('Georges Goetz', 'geo.goetz@gmail.com'),
)

MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## GENERAL CONFIGURATION
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name although not all
# choices may be available on all operating systems. On Unix systems, a value
# of None will cause Django to use the same timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html.
LANGUAGE_CODE = 'en-us'

# The ID, as an integer, of the current site in the django_site database table.
# This is used so that application data can hook into specific site(s) and a
# single database can manage content for multiple sites.
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True
########## END GENERAL CONFIGURATION


########## STATIC FILE CONFIGURATION
STATIC_ROOT = 'staticfiles'

# URL prefix for static files.
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files.
STATICFILES_DIRS = (
    normpath(join(DJANGO_ROOT, 'static')),
)

# List of finder classes that know how to find static files in various
# locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
########## END STATIC FILE CONFIGURATION


########## TEMPLATE CONFIGURATION
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

# Directories to search when loading templates.
TEMPLATE_DIRS = (
    normpath(join(DJANGO_ROOT, 'templates')),
)
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## APP CONFIGURATION
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Admin panel and documentation.
    'django.contrib.admin',
    'django.contrib.admindocs',

    # site-specific apps
    'cfsite.apps.crawlers',
    'cfsite.apps.events',
)
########## END APP CONFIGURATION


########## URL CONFIGURATION
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION

