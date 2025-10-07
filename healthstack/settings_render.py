"""
Production settings for Mahima Medicare on Render.com
Use this by setting: DJANGO_SETTINGS_MODULE=healthstack.settings_render
"""

from .settings import *
import os

# Override DEBUG for production
DEBUG = False

# CRITICAL: Force ALLOWED_HOSTS for Render.com
ALLOWED_HOSTS = [
    'mahimamedicare.onrender.com',
    '*.onrender.com',
    'localhost', 
    '127.0.0.1',
    '0.0.0.0'
]

# Add any additional hosts from environment
env_hosts = os.environ.get('ALLOWED_HOSTS', '')
if env_hosts:
    additional_hosts = [host.strip() for host in env_hosts.split(',') if host.strip()]
    ALLOWED_HOSTS.extend(additional_hosts)

# Remove duplicates
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))

# Force production settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'mahima-medicare-render-fallback-key-2025')

# Database configuration for Render.com
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        DATABASES = {
            'default': dj_database_url.parse(database_url)
        }

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = False  # Render handles this
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('SMTP_USER', 'marklegend029@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD', 'lkkvkybyhftvppvc')

# Logging configuration
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
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

print(f"Render Production Settings Loaded - ALLOWED_HOSTS: {ALLOWED_HOSTS}")