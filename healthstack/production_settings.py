# Production Settings for Mahima Medicare
# Your Health Partner

import os
from .settings import *

# Security Settings
DEBUG = False
ALLOWED_HOSTS = [
    'mahima-medicare.onrender.com',
    'mahimamedicare.co.in',
    'www.mahimamedicare.co.in',
    '127.0.0.1',
    'localhost'
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database Configuration for Production
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }

# Static Files for Production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files for Production
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email Configuration (if needed)
if 'EMAIL_HOST_PASSWORD' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'mahimamedicare01@gmail.com')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Logging Configuration
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
}

# Company Information
COMPANY_INFO = {
    'name': 'Mahima Medicare',
    'tagline': 'Your Health Partner',
    'phone': '+91 8763814619',
    'email': 'mahimamedicare01@gmail.com',
    'address': 'Barkoliya Bajar, Orti, Cuttack, 754209',
    'gstin': '21AXRPN9340C1ZH',
    'website': 'mahimamedicare.co.in'
}
