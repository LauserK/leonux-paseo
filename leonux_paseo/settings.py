import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1frzutblup=$4^zk2b(mw%d(b+_*q74z^@t0jjkr+2m@29)g1_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('REPORTES_DEBUG', False)

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'articulos',
    'usuarios',
    'ventas'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'leonux_paseo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'public/templates'),],
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

WSGI_APPLICATION = 'leonux_paseo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

if DEBUG == False:
    DATABASES = {
        'leonux': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '00000001',
            'USER': 'root',
            'PASSWORD': '123',
            'HOST': '10.10.0.199',
            'PORT': '3306',
        },
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'report-system',
            'USER': 'root',
            'PASSWORD': '123',
            'HOST': '10.10.0.199',
            'PORT': '3306',
        }
    }
else:
    DATABASES = {
        'leonux': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('LEONUX_DB_NAME', '00000001'),
            'USER':os.environ.get('LEONUX_DB_USER', 'root'),
            'PASSWORD': os.environ.get('LEONUX_DB_PASSWORD', ''),
            'HOST': os.environ.get('LEONUX_DB_HOST', '127.0.0.1'),
            'PORT': '3306',
        },
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('REPORTES_DB_NAME', 'report-system'),
            'USER':os.environ.get('REPORTES_DB_USER', 'root'),
            'PASSWORD': os.environ.get('REPORTES_DB_PASSWORD', ''),
            'HOST': os.environ.get('REPORTES_DB_HOST', '127.0.0.1'),
            'PORT': '3306',
        }
    }




# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Caracas'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

if DEBUG == False:
    STATIC_ROOT = '/var/www/reportes/static'
    STATIC_URL = 'http://10.10.0.70/statir/'
else:
    STATIC_URL = '/static/'

# Media files
if DEBUG == False:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'public/media')
    MEDIA_URL  = 'http://10.10.0.70/mediar/'
else:
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'public/media')

LOGIN_REDIRECT_URL = '/'

AUTH_USER_MODEL = 'usuarios.User'
