#
# central/utils/gpio.py
#

from central.utils import (
    InvalidPinNomenclatureException, InvalidDirectionException)


class GPIO(object):
    PULLNONE = 0
    PULLUP = 1
    PULLDOWN = -1
    IN = 'in'
    OUT = 'out'
    _ACTIVE_LOW = 'active_low'
    _DIRECTION = 'direction'
    _EDGE = 'edge'
    _UEVENT = 'uevent'
    _VALUE = 'value'
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
    __GPIO_PATH = '/sys/class/gpio'

    def __init__(self):
        pass

    def getPinNumber(self, pin):
        result = 0

        if not isinstance(pin, basestring):
            raise InvalidPinNomenclatureException(pin)

        head, delimiter, tail = pin.partition('_')
        head = head.upper()

        if head[0] == 'P' and head[-1].isdigit() and tail.isdigit():
            result = self.__PIN_MAP.get(int(head[-1]), {}).get(tail, 0)
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

    def setPinMode(pin, direction=OUT, pull=PULLNONE):
        """
        Sets digital pin mode.

        pin       -- Any of the pin designation types (GPIO1_1, GPIO_33, or
                     P8_24).
        direction -- Sets the pin to either input (GPIO.IN) or output (GPIO.OUT)
                     is default.
        pull      -- Set the internal resister to pull up (GPIO.PULLUP) or pull
                     down (GPIO.PULLDOWN) or neither (GPIO.PULLNONE) is default.
        """
        if direction not in (self.IN, self.OUT):
            raise InvalidDirectionException(pin)

        gpioId = self.getPinNumber(pin)
        self._writePin(gpioId, direction, file=self._DIRECTION)

    def _readPin(self, gpioId, file=_VALUE):
        path = os.path.join(self.__GPIO_PATH, 'gpio{}'.format(gpioId), file)
        fd = os.open(path, os.O_RDONLY)
        result = os.read(fd, 256)
        os.close(fd)
        return result

    def _writePin(self, gpioId, value, file=_VALUE):
        path = os.path.join(self.__GPIO_PATH, 'gpio{}'.format(gpioId), file)
        fd = os.open(path, os.O_WRONLY)
        numBytes = os.write(fd, value)
        os.close(fd)

        if numBytes != len(value):
            raise IOError("Wrong number of bytes witten to {}, wrote: {}, "
                          "should have been: {}".format(
                              path, numBytes, len(value)))
