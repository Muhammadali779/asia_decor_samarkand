import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 📁 .env faylini yuklash (Bu usul xavfsizroq va aniqroq)
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 🔐 SECRET KEY
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-please-change-this-in-production'
)

# 🐞 DEBUG
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# 🌐 ALLOWED HOSTS
ALLOWED_HOSTS = ['*','']

_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
if _render_host:
    ALLOWED_HOSTS += [_render_host]

# 📦 APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

# ⚙️ MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'asia_decor.urls'

# 🧩 TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# 🚀 WSGI
WSGI_APPLICATION = 'asia_decor.wsgi.application'

# 🗄 DATABASE — PostgreSQL
# Render'da DATABASE_URL avtomatik bo'ladi, lokalda .env dan o'qiydi
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True, # Render bazalari uchun majburiy
        )
    }
else:
    # Lokal xatolikni oldini olish uchun zaxira (fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'asia_decor_db'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# 🔐 PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 LANGUAGE
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# 📁 STATIC
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

_static_dir = BASE_DIR / 'static'
if _static_dir.exists():
    STATICFILES_DIRS = [_static_dir]
else:
    STATICFILES_DIRS = []

# ⚡ WhiteNoise (Static fayllar siqilishi uchun)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 📁 MEDIA
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🔢 DEFAULT FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🤖 TELEGRAM BOT SOZLAMALARI
USER_BOT_TOKEN = os.environ.get('USER_BOT_TOKEN', '')
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '')

SITE_URL = os.environ.get(
    'SITE_URL',
    'https://asia-decor-samarkand-3.onrender.com'
)

ALLOWED_ADMIN_IDS = [
    x.strip() for x in os.environ.get('ALLOWED_ADMIN_IDS', '').split(',')
    if x.strip()
]