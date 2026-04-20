import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-local-dev-only-key")
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "finance",
]

USE_S3_MEDIA_STORAGE = env_bool("USE_S3_MEDIA_STORAGE", False)
if USE_S3_MEDIA_STORAGE:
    INSTALLED_APPS.append("storages")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pfm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pfm.wsgi.application"


if os.getenv("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB"),
            "USER": os.getenv("POSTGRES_USER", ""),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_DIR = BASE_DIR / "static"
STATICFILES_DIRS = [STATIC_DIR] if STATIC_DIR.exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
ENABLE_CLOUD_INTEGRATIONS = env_bool("ENABLE_CLOUD_INTEGRATIONS", False)
AWS_S3_AUDIT_BUCKET = os.getenv("AWS_S3_AUDIT_BUCKET", "")
AWS_S3_MEDIA_BUCKET = os.getenv("AWS_S3_MEDIA_BUCKET", AWS_S3_AUDIT_BUCKET)
AWS_S3_MEDIA_LOCATION = os.getenv("AWS_S3_MEDIA_LOCATION", "media")
AWS_DEFAULT_ACL = None
AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN", "")
AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL", "")
AWS_CLOUDWATCH_NAMESPACE = os.getenv("AWS_CLOUDWATCH_NAMESPACE", "PFM/Application")
AWS_CONFIG_PARAMETER_NAME = os.getenv("AWS_CONFIG_PARAMETER_NAME", "")
EXPENSE_ALERT_THRESHOLD = os.getenv("EXPENSE_ALERT_THRESHOLD", "500.00")

if USE_S3_MEDIA_STORAGE and AWS_S3_MEDIA_BUCKET:
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False

    if AWS_REGION == "us-east-1":
        MEDIA_URL = f"https://{AWS_S3_MEDIA_BUCKET}.s3.amazonaws.com/{AWS_S3_MEDIA_LOCATION}/"
    else:
        MEDIA_URL = f"https://{AWS_S3_MEDIA_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{AWS_S3_MEDIA_LOCATION}/"

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": AWS_S3_MEDIA_BUCKET,
                "location": AWS_S3_MEDIA_LOCATION,
                "default_acl": AWS_DEFAULT_ACL,
                "querystring_auth": AWS_QUERYSTRING_AUTH,
                "file_overwrite": AWS_S3_FILE_OVERWRITE,
                "region_name": AWS_REGION,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
