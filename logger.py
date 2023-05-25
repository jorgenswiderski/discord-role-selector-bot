# logger.py
import logging
import logging.config

logging_config = {
    "version": 1,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        },
        "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "logs/bot.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,  # Keep up to 30 past log files.
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    "loggers": {"hikari": {"level": "INFO"}, "lightbulb": {"level": "INFO"}},
}


def init_logging():
    logging.config.dictConfig(logging_config)
