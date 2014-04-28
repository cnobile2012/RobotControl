#
# central/utils/basegpio.py
#

import re, os, dircache

from .exceptions import (
    InvalidPinNomenclatureException, InvalidArgumentsException)


class BaseGPIO(object):
    __DIRS_RE = re.compile(r'^gpio\d{1,3}/$')
    __EXPORT = 'export'
    __UNEXPORT = 'unexport'
    __PIN_MAP = {8: { 3: 38,  4: 39,  5: 34,  6: 35,  7: 66,  8: 67,  9: 69,
                     10: 68, 11: 45, 12: 44, 13: 23, 14: 26, 15: 47, 16: 46,
                     17: 27, 18: 65, 19: 22, 20: 63, 21: 62, 22: 37, 23: 36,
                     24: 33, 25: 32, 26: 61, 27: 86, 28: 88, 29: 87, 30: 89,
                     31: 10, 32: 11, 33:  9, 34: 81, 35:  8, 36: 80, 37: 78,
                     38: 79, 39: 76, 40: 77, 41: 74, 42: 75, 43: 72, 44: 73,
                     45: 70, 46: 71},
                 9: {11: 30, 12: 60, 13: 31, 14: 40, 15: 48, 16: 51, 17:  4,
                     18:  5, 21:  3, 22:  2, 23: 49, 24: 15, 25: 117, 26: 14,
                     27: 125, 28: 123, 29: 121, 30: 122, 31: 120, 41: 20, 42: 7}
                 }
    __VALID_PINS = (
        2, 3, 4, 5, 7, 8, 9, 10, 11, 14, 15, 20, 22, 23, 26, 27, 30, 31, 32,
        33, 34, 35, 36, 37, 38, 39, 40, 44, 45, 46, 47, 48, 49, 51, 60, 61,
        62, 63, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
        80, 81, 86, 87, 88, 89, 117, 120, 121, 122, 123, 125)
    _GPIO_PATH = '/sys/class/gpio'

    def __init__(self):
        pass

    def _exportPin(self, gpioId):
        result = False
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId))

        if not os.path.exists(path):
            path = os.path.join(self._GPIO_PATH, self.__EXPORT)
            self._writePin(path, gpioId)
            result = True

        return result

    def _unexportPin(self, gpioId):
        result = False
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId))

        if os.path.exists(path):
            path = os.path.join(self._GPIO_PATH, self.__UNEXPORT)
            self._writePin(path, gpioId)
            result = True

        return result

    def cleanup(self, pin=None):
        result = False

        if pin is not None:
            gpioId = self._getGpioId(pin)
            result = self._unexportPin(gpioId)
        elif any([self._unexportPin(gpioId)
                  for gpioId in self._findActivePins()]):
            result = True

        return result

    def _findActivePins(self):
        dirs = dircache.listdir(self._GPIO_PATH)
        dircache.annotate(self._GPIO_PATH, dirs)
        return [d[4:-1] for d in dirs if self.__DIRS_RE.search(d)]

    def _getGpioId(self, pin):
        result = 0

        if not isinstance(pin, basestring):
            raise InvalidPinNomenclatureException(pin)

        head, delimiter, tail = pin.partition('_')
        head = head.upper()

        if (len(head) == 2 and head[0] == 'P' and
            head[-1].isdigit() and tail.isdigit()):
            result = self.__PIN_MAP.get(int(head[-1]), {}).get(
                int(tail), 0)
        elif head == 'GPIO' and tail.isdigit():
            result = int(tail)
        elif (len(head) == 5 and head[:4] == 'GPIO' and
              head[-1].isdigit() and tail.isdigit()):
            result = int(head[-1]) * 32 + int(tail)
        else:
            raise InvalidPinNomenclatureException(pin)

        if result not in self.__VALID_PINS:
            raise InvalidPinNomenclatureException(pin)

        return result

    def _readPin(self, path, bytes=128):
        fd = os.open(path, os.O_RDONLY)
        result = os.read(fd, bytes)
        os.close(fd)
        return result

    def _writePin(self, path, value):
        value = str(value)
        fd = os.open(path, os.O_WRONLY)
        numBytes = os.write(fd, value)
        os.close(fd)

        if numBytes != len(value):
            raise IOError("Wrong number of bytes witten to {}, wrote: {}, "
                          "should have been: {}".format(
                              path, numBytes, len(value)))