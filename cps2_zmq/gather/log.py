"""
Default logging rules.
"""
import logging
import logging.config

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {

    },
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

def configure():
    logging.config.dictConfig(DEFAULT_LOGGING)
