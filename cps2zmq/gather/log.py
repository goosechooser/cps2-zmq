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

    }
}

def configure(logger, fhandler=False):
    if fhandler:
        fname = '.'.join([logger, 'log'])
        fhandler = {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': fname
        }

        DEFAULT_LOGGING['handlers']['file'] = fhandler

    loggers = {
        logger : {
            'level': 'DEBUG',
            'handlers': DEFAULT_LOGGING['handlers'],
            'propagate': False
        }
    }

    DEFAULT_LOGGING['loggers'] = loggers

    logging.config.dictConfig(DEFAULT_LOGGING)

    return logging.getLogger(logger)
