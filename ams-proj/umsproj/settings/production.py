"""
Production settings for umsproj.
"""

from .base import *


ENV = "production"

IS_PRODUCTION = True

DEBUG = False


# ---------------------------------------------------------------------------
# HOSTS
# ---------------------------------------------------------------------------

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ["ALLOWED_HOSTS"].split(",")
    if host.strip()
]


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ["CSRF_TRUSTED_ORIGINS"].split(",")
    if origin.strip()
]


# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------

import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ["DATABASE_URL"],
        conn_max_age=600,
        ssl_require=(
            os.environ.get(
                "DB_SSL_REQUIRE",
                "False",
            )
            == "True"
        ),
    )
}

DATABASES["default"]["ENGINE"] = (
    "django_prometheus.db.backends.postgresql"
)


# ---------------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------------

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = os.environ["EMAIL_HOST"]

EMAIL_PORT = int(
    os.environ.get(
        "EMAIL_PORT",
        587,
    )
)

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]

EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = "DENY"