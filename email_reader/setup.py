from logging import config
import logging
import warnings

def configure_get_log():
    warnings.filterwarnings("ignore")

    config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,  # Disable existing loggers before applying new configuration
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
                }
            },
            "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": "logs.log",
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "loggers": {
                "root": {
                    "level": logging.INFO,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "sqlalchemy": {  # Disable SQLAlchemy logs explicitly here
                    "level": logging.CRITICAL,
                    "handlers": ["console"],
                },
                "sqlalchemy.engine": {  # Disable engine logs explicitly here
                    "level": logging.CRITICAL,
                    "handlers": ["console"],
                },
                "sqlalchemy.orm": {  # Disable ORM logs explicitly here
                    "level": logging.CRITICAL,
                    "handlers": ["console"],
                },
                "sqlalchemy.dialects": {  # Disable dialect logs explicitly here
                    "level": logging.CRITICAL,
                    "handlers": ["console"],
                },
                "psycopg2": {  # Disable psycopg2 logs explicitly here
                    "level": logging.CRITICAL,
                    "handlers": ["console"],
                },
            },
        }
    )
    log = logging.getLogger("root")
    return log

# Configure logging
log = configure_get_log()

