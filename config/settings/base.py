import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKUP = '1.10'
DESIRED_IMAGE_SIZE = 350

AWS_STATIC_BUCKET_NAME = 'pixidesk-development'
AWS_MEDIA_BUCKET_NAME = "pixidesk-development-media"
AWS_S3_REGION_NAME = 'us-east-1'

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'config.settings.custom_storage.StaticStorage'

MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'config.settings.custom_storage.MediaStorage'


INSTALLED_APPS = [
    'corsheaders',
    'djmoney',
    'django_celery_results',
    'django_json_widget',
    'django_celery_beat',
    'storages',
    # 'grappelli',

    'debug_toolbar',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',

    'Accounts',
    'Addresses',
    'Carts',
    'Cards',
    'config',
    'CustomerProfiles',
    'FinishSurfaces',
    'MailingList',
    'Orders',
    'Plans',
    'Products',
    'ProductFilter',
    'Profiles',
    'Ratings',
    'Scraper',
    'Scraper.ScraperFinishSurface',
    'Scraper.ScraperCleaner'
]

# CELERY STUFF
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'US/Eastern'

ROOT_URLCONF = 'config.urls'

DATABASE_ROUTERS = ['config.settings.db_routers.ScraperRouter']

SITE_ID = 1

GMAPS_API_KEY = 'AIzaSyD1ehaLv6OBqN3m_qjif2N7Gge0PDP5ams'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

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




LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'Accounts.User'
