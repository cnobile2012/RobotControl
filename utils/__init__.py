#
# utils/__init__.py
#

import os
import logging
from logging_config import ConfigLogger


def isRoot(logger=''):
    result = True
    log = logging.getLogger(logger)

    if os.getuid() != 0:
        result = False
        log.critical("You must be root to run this application, found user: %s",
                     os.environ.get('LOGNAME'))

    return result


def getBasePath():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
