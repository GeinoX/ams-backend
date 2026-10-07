"""
Development settings for umsproj.
"""

from .base import *


ENV = "development"

IS_PRODUCTION = False

DEBUG = True


# ---------------------------------------------------------------------------
# HOSTS
# ---------------------------------------------------------------------------

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "imitation-quaintly-empirical.ngrok-free.dev"
]


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://127.0.0.1:8000",
    "https://localhost:8000",
]

# from notifications.services.email_service import EmailService
# EmailService.send("63a26687-a453-404e-a389-3de528c9e65a")

# print(settings.EMAIL_BACKEND, settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_USE_TLS)
# print(repr(settings.EMAIL_HOST_USER), bool(settings.EMAIL_HOST_PASSWORD), settings.DEFAULT_FROM_EMAIL)
# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ---------------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------------

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

# EMAIL_HOST = ""

# EMAIL_PORT = 0

# EMAIL_USE_TLS = False

# EMAIL_HOST_USER = ""

# EMAIL_HOST_PASSWORD = ""

# DEFAULT_FROM_EMAIL = "development@localhost"


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------

SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0

SECURE_HSTS_INCLUDE_SUBDOMAINS = False

SECURE_HSTS_PRELOAD = False

SECURE_PROXY_SSL_HEADER = None


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = True


# ---------------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------------

STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.StaticStaticFilesStorage"
)