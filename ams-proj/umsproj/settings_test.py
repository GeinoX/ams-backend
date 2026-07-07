"""
Test settings for umsproj project.
Used by GitHub Actions and local test runs.
Overrides production settings with fast, isolated, dependency-free alternatives.
"""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# IMPORT EVERYTHING FROM MAIN SETTINGS FIRST
# ---------------------------------------------------------------------------
from .settings import *

# ---------------------------------------------------------------------------
# CORE
# ---------------------------------------------------------------------------
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "test-secret-key-not-real-do-not-use-in-production")

ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# DATABASE — use in-memory SQLite, no server needed, fast, auto-destroyed
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ---------------------------------------------------------------------------
# EMAIL — print to console, no real emails sent during tests
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST_USER = "test@test.com"
EMAIL_HOST_PASSWORD = "testpassword"
DEFAULT_FROM_EMAIL = "test@test.com"

# ---------------------------------------------------------------------------
# CELERY — run tasks synchronously so tests don't have to wait
# ---------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

# ---------------------------------------------------------------------------
# SENTRY — disable completely during tests
# ---------------------------------------------------------------------------
SENTRY_DSN = None

# ---------------------------------------------------------------------------
# CLOUDINARY — disable during tests, use local media storage
# ---------------------------------------------------------------------------
CLOUDINARY_CLOUD_NAME = None
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# remove cloudinary from INSTALLED_APPS if it was added by settings.py
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ["cloudinary", "cloudinary_storage"]]

# ---------------------------------------------------------------------------
# PROMETHEUS — disable during tests
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # ← plain sqlite, no prometheus wrapper
        "NAME": ":memory:",
    }
}

# ---------------------------------------------------------------------------
# SECURITY — relax for tests
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# ---------------------------------------------------------------------------
# LOGGING — minimal during tests
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",  # ← only show warnings and errors during tests
    },
}

# ---------------------------------------------------------------------------
# STATICFILES — disable manifest storage during tests
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# ---------------------------------------------------------------------------
# PASSWORD HASHERS — use fast hasher during tests
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",  # ← much faster than bcrypt for tests
]