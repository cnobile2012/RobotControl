#
# central/utils/containers.py
#

import os, logging


from .gpio import GPIO


class BaseContainer(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Pin(GPIO, BaseContainer):

    def __init__(self, pin, logger=None, level=logging.DEBUG):
        super(Pin, self).__init__(logger=logger, level=level)
        self._pin = pin
        self._gpioId = self._getGpioId(pin)
        self._fd = self.open()
        self._direction = ""
        self._edge = ""

    def open(self):
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(self._gpioId),
                            self._VALUE)
        return self._openPin(path)

    def close(self):
        os.close(self._fd)
        self._fd = None
        self._direction = ""
        self._edge = ""

    @property
    def is_closed(self):
        return self._fd and True or False

    def fileno(self):
        return self._fd

    @property
    def direction(self):
        if not self._direction:
            self._direction = self.getDirection(self._pin)

        return self._direction

    @property
    def edge(self):
        if not self._edge:
            self._edge = self.getEdge(self._pin)

        return self._edge
