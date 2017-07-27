"""
Default logging rules.
"""
import sys
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
        'file':{

        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

WORKER_LOGGING = {
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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'default',
            # 'filename': None
        }
    },
    # 'root': {
    #     'level': 'INFO',
    #     'handlers': ['console']
    # }
}


def configure():
    logging.config.dictConfig(DEFAULT_LOGGING)

def configure_worker(worker):
    name = '.'.join([worker.__class__.__name__, str(worker.idn, encoding='utf-8')])
    fname = '.'.join([name, 'log'])
    WORKER_LOGGING['handlers']['file']['filename'] = fname
    logger = {
        name : {
            'level': 'DEBUG',
            'handlers': WORKER_LOGGING['handlers']
        }
    }
    WORKER_LOGGING['loggers'] = logger
    logging.config.dictConfig(WORKER_LOGGING)


