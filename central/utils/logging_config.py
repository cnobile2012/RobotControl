#
# utils/logging_config.py
#

import os
import logging


class ConfigLogger(object):
    """
    Setup some basic logging. This could get more sophisticated in the future.
    """
    _DEFAULT_FORMAT = ("%(asctime)s %(levelname)s %(module)s %(funcName)s "
                       "[line:%(lineno)d] %(message)s")

    def __init__(self, logPath):
        self._logPath = logPath.rstrip('/')
        self._format = self._DEFAULT_FORMAT

    def config(self, loggerName, filename=None, level=logging.INFO):
        """
        loggerName is not used yet.
        """
        if filename is not None:
            filePath = os.path.join(self._logPath, filename)
        else:
            filePath = None

        return logging.basicConfig(filename=filePath, format=self._format,
                                   level=level)


    def setFormat(self, fmt=None, default=_DEFAULT_FORMAT):
        """
        Must be called before the config method or it will have no effect.
        """
        if not fmt: fmt = default
        self._format = fmt
