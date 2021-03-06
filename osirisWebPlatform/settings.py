"""
Django settings for osirisWebPlatform project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import osirisWebPlatform.keys.database as database
import osirisWebPlatform.keys.secret_key as secretKey

from django.utils.translation import ugettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secretKey.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SERVER_IP = u'104.236.142.96'
ALLOWED_HOSTS = [SERVER_IP, u'172.17.57.156', u'127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_crontab',
    'myadmin',
    'scene',
    'cmmmodel',
    'viz',
    'bowerapp',
    'energycentermodel'
]

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'osirisWebPlatform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'osirisWebPlatform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = database.DATABASES

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGES = (
#    ('en', _('English')),
    ('es', _('Spanish')),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# User url
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/admin/scene/scene/'

# To storage excel files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

KEY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys')

# to manipulate remote execution
PYTHON_COMMAND = "PYTHONPATH={} {}".format(BASE_DIR,
                                           os.path.join(BASE_DIR, 'myenv', 'bin', 'python'))
# folder to save model answer sent by cmm cluster
MODEL_OUTPUT_PATH = os.path.join(MEDIA_ROOT, "modelOutput")

# cluster info
CLUSTER_URL = 'leftraru.nlhpc.cl'
CLUSTER_USER = 'fhernandez'

# crontab configuration
CRONJOBS = [
    ('*/1 * * * *', 'cmmmodel.cron.checkExecutionStatus.check_execution_is_running', '>> /tmp/task.log 2>&1')
]
CRONTAB_LOCK_JOBS = True