import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

# 🔐 SECRET KEY
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-please-change-this-in-production'
)

# 🐞 DEBUG
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# 🌐 ALLOWED HOSTS — to'liq ro'yxat
ALLOWED_HOSTS = [
    '*',  # Render.com uchun (yoki aniq domen)
]

# Aniq domen variantlari (ixtiyoriy, agar * ishlamasa)
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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static uchun
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

# 🗄 DATABASE
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

# 📁 STATIC — static papka yo'q bo'lsa ham xato bermaydi
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Faqat papka mavjud bo'lsa qo'shamiz
_static_dir = BASE_DIR / 'static'
if _static_dir.exists():
    STATICFILES_DIRS = [_static_dir]
else:
    STATICFILES_DIRS = []

# ⚡ WhiteNoise
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
