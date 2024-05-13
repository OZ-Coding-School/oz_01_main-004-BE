from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*", "https://cookbap.store"]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("DB_HOST"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "PORT": env("DB_PORT"),
    }
}

CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:3000"]

CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_ALLOW_ALL = True

CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:3000", "https://cookbap.store"]

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True
