from pathlib import Path
import os
from dotenv import load_dotenv
from django.urls import reverse_lazy
import dj_database_url



# Load environment variables from a .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret Key (stored in environment variable)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-fallback-secret-key')

# Debug Mode (toggle via environment variable)
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Allowed Hosts (add production domain when deploying)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

# Installed Applications
INSTALLED_APPS = [
    'blog.apps.BlogConfig',
    'users.apps.UsersConfig',
    'rest_framework',
    'crispy_forms',
    'tinymce',
    'crispy_bootstrap5',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL Configuration
ROOT_URLCONF = 'k_django.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':[BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.views.sidebar_context',
            ],
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'k_django.wsgi.application'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
DATABASES['default'] = dj_database_url.config(
    default=os.getenv("DATABASE_URL"),
    conn_max_age=600,
    ssl_require=True
)


# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization & Timezone Settings
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Crispy Forms (Bootstrap 5)
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Static Files (CSS, JS)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Media Files (Uploaded Content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # ✅ Changed from hardcoded Windows path

# Default Primary Key Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication Redirects
from django.urls import reverse_lazy

# Authentication Redirects
LOGIN_REDIRECT_URL = reverse_lazy('blog-home')
LOGOUT_REDIRECT_URL = reverse_lazy('login')
LOGIN_URL = reverse_lazy('login')


# Email Configuration (Moved to Environment Variables)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # Use an app password for security

TINYMCE_DEFAULT_CONFIG = {
    'height': 400,
    'width': 800,
    'menubar': True,
    'plugins': 'advlist autolink lists link image charmap print preview anchor '
                'searchreplace visualblocks code fullscreen insertdatetime media table code help wordcount',
    'toolbar': 'undo redo | formatselect | bold italic backcolor | '
                'alignleft aligncenter alignright alignjustify | '
                'bullist numlist outdent indent | removeformat | help | code',
    'branding': False,
}