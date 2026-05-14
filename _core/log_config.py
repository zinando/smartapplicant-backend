import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "[%(asctime)s] [%(levelname)s] "
                "[%(name)s:%(lineno)d] "
                "[PID:%(process)d] %(message)s"
            ),
        },
    },

    "handlers": {
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "django.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 10,
            "formatter": "standard",
        },
        "app_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "standard",
        },
    },

    "loggers": {
        # Django framework logs
        "django": {
            "handlers": ["django_file"],
            "level": "INFO",
            "propagate": False,
        },

        # Your application (replace with your root app module)
        "smartapplicant": {
            "handlers": ["app_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}