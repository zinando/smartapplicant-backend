from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
# import dj_database_url
#import resource

# Load environment variables from .env file
load_dotenv(override=True)

# print(f"Password: {os.getenv('POSTGRES_PASSWORD')}")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# Disable Django features that eat memory
DEBUG = False
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}  # Reduce log verbosity

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    '146.19.133.88',
    "smartapplicant.net",  # Your actual production domain
    ".smartapplicant.net"  # Allows all subdomains
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Dev
    "http://146.19.133.88",   # <-- This is the frontend origin!
    "http://146.19.133.88:8000",  # Backend (optional, not required)
    "https://smartapplicant.net",
    "https://apps.smartapplicant.net",
    "https://www.smartapplicant.net",
    "https://api.smartapplicant.net",
]

CORS_ALLOW_CREDENTIALS = False 
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'api',
    'auth_user',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

# Reduce memory usage
# SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"  # Faster than DB
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"  # Smaller footprint

# resource.setrlimit(resource.RLIMIT_AS, (400_000_000, 400_000_000))  # Hard cap at 400MB

# Media files (for resume uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# _core/settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB limit
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB limit

ROOT_URLCONF = '_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEMPLATES[0]['OPTIONS']['debug'] = False

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'SIGNING_KEY': os.getenv('JWT_SIGNING_KEY'),
}

WSGI_APPLICATION = '_core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'), 
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),  # Use environment variable for password
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': '5432',
    }
}

# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.environ.get('DATABASE_URL', 'DATABASE_URL_EXTERNAL'),
#         conn_max_age=600,
#         ssl_require=True
#     )
# }

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

AUTH_USER_MODEL = 'auth_user.CustomUser'

AUTHENTICATION_BACKENDS = [
    'auth_user.authentication.EmailAuthBackend',  # Custom backend
    'django.contrib.auth.backends.ModelBackend',  # Default Django backend
]


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery settings
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')  # Replace with Render/Redis Cloud URL
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')  # Replace with Render/Redis Cloud URL
CELERY_TIMEZONE = 'UTC'

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')  # Default to SMTP backend
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')  # Default to Gmail SMTP
EMAIL_PORT = os.getenv('EMAIL_PORT', '587')  # Default SMTP port for TLS
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')  # Convert to boolean
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_SENDER')
