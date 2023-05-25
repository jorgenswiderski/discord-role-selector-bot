# logger.py
import logging
import logging.config

logging_config = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "logs/bot.log",
            "mode": "a"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    },
    "loggers": {
        "hikari": {
            "level": "INFO"
        },
        "lightbulb": {
            "level": "INFO"
        }
    }
}

def init_logging():
    logging.config.dictConfig(logging_config)