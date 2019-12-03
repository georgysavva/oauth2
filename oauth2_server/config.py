import logging.config
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_APPLICATIONS = [
    {
        'client_id': '1234',
        'client_secret': 'qwerty'
    }
]
USE_JSON_LOGGER_FORMATTER = False

try:
    # This file won't get into git and docker image.
    # Environment specific settings stored there.
    # Further improvement: use regular json/yaml config file instead
    from configs.application_config import *
except ImportError:
    pass
# Further improvement: create a separate json/yaml config file with default logging configuration.
# And another one for environment specific logging.
# It will allow adjust logging behaviour more precisely
logging_conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s]:%(levelname)s:%(name)s: %(message)s',
        },
    },
    'handlers': {'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}
# Further improvement: create a separate json/yaml logging config file with
if USE_JSON_LOGGER_FORMATTER:
    logging_conf['formatters']['default']['class'] = 'pythonjsonlogger.jsonlogger.JsonFormatter'

logging.config.dictConfig(logging_conf)