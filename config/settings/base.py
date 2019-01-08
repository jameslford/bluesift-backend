import os
import decimal
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKUP = '1.10'
DESIRED_IMAGE_SIZE = 350

ALT_SAFE_PATH = 'D:\\BBdata\\product_images'

# password is robertmurray
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'djmoney',
    'storages',
    'corsheaders',

    'rest_framework',
    'rest_framework.authtoken',

    'Accounts',
    'Addresses',
    'Carts',
    'Cards',
    'config',
    'Orders',
    'Plans',
    'Products',
    'Profiles',

]




ROOT_URLCONF = 'config.urls'

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

