import logging.config
import os

USE_JSON_LOGGER_FORMATTER = False

JWT_SIGNATURE_SECRET_KEY = '604fe435c2a4d63046741c572023c448b76af554c824a2065d53563fac168cd8'
DEFAULT_USERS_SCOPE = ['/current_time', '/epoch_time']
DEFAULT_APPLICATIONS = [
    {
        'client_id': '1234',
        'client_secret': 'qwerty'
    }
]

try:
    # This file won't get into git and docker image.
    # Environment specific settings stored there.
    # Further improvement: use regular json/yaml config file instead
    from configs.application_config import *
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_SCHEMAS_DIR = os.path.join(BASE_DIR, 'json_schemas')
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
