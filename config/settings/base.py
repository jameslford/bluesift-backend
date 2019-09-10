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
    'django_celery_results',
    'django_json_widget',
    'django_celery_beat',
    'storages',
    'ipware',
    # 'grappelli',

    'debug_toolbar',
    'django.contrib.admindocs',
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
    'Analytics',
    'Cards',
    'Carts',
    'config',
    'Groups',
    'MailingList',
    'Orders',
    'Plans',
    'ProductFilter',
    'Products',
    'Profiles',
    'Ratings',
    'Scraper',
    'Scraper.ScraperFinishSurface',
    'Scraper.ScraperCleaner',
    'SpecializedProducts',
    'UserProductCollections',
    'UserProducts'
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

IPWARE_META_PRECEDENCE_ORDER = (
        'HTTP_X_FORWARDED_FOR',
        'X_FORWARDED_FOR',
        'CF-Connecting-IP',
        'HTTP_CLIENT_IP',
        'HTTP_X_REAL_IP',
        'HTTP_X_FORWARDED',
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED_FOR',
        'HTTP_FORWARDED',
        'HTTP_VIA',
        'REMOTE_ADDR',
    )

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
