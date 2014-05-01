#
# central/utils/gpio.py
#

import os, logging

from .exceptions import (
    InvalidPinNomenclatureException, InvalidDirectionException,
    InvalidEdgeException, InvalidArgumentsException)
from .basegpio import BaseGPIO


class GPIO(BaseGPIO):
    IN = 'in'
    OUT = 'out'
    RISING = 'rising'
    FALLING = 'falling'
    BOTH = 'both'
    HIGH = 1
    LOW = 0
    _ACTIVE_LOW = 'active_low'
    _DIRECTION = 'direction'
    _EDGE = 'edge'
    _UEVENT = 'uevent'
    _VALUE = 'value'

    def __init__(self, logger=None, level=logging.DEBUG):
        super(GPIO, self).__init__(logger=logger, level=level)

    def setPinMode(self, pin, direction=None, edge=None):
        """
        Sets digital pin mode. If previously no exported this method shall
        return 'True' else if already exported the return value shall be
        'False' unless either or both direction or edge is passed in, in which
        case the return value shall be 'True'.

        pin       -- Any of the pin designation types. ex. GPIO1_1, GPIO_33, or
                     P8_24.
        direction -- Sets the pin to either input (GPIO.IN) or output (GPIO.OUT)
                     is default.
        edge      -- Sets the pin trigger edge to GPIO.RISING, GPIO.FALLING, or
                     GPIO.BOTH.
        """
        self._log.debug("pin: %s, direction: %s, edge: %s",
                        pin, direction, edge)

        if direction and direction not in (self.IN, self.OUT):
            raise InvalidDirectionException(pin)

        if edge and edge not in (self.RISING, self.FALLING, self.BOTH):
            raise InvalidEdgeException(pin)

        gpioId = self._getGpioId(pin)
        result = self._exportPin(gpioId)

        if direction:
            path = os.path.join(
                self._GPIO_PATH, 'gpio{}'.format(gpioId), self._DIRECTION)
            self._writePin(path, direction)
            result = True

        if edge:
            path = os.path.join(
                self._GPIO_PATH, 'gpio{}'.format(gpioId), self._EDGE)
            self._writePin(path, edge)
            result = True

        return result

    def setPinDirection(self, pin, direction):
        gpioId = self._getGpioId(pin)
        path = os.path.join(
            self._GPIO_PATH, 'gpio{}'.format(gpioId), self._DIRECTION)
        self._write(path, direction)

    def getPinDirection(self, pin):
        gpioId = self._getGpioId(pin)
        path = os.path.join(
            self._GPIO_PATH, 'gpio{}'.format(gpioId), self._DIRECTION)
        return self._readPin(path)

    def setPinEdge(self, pin, edge):
        gpioId = self._getGpioId(pin)
        path = os.path.join(
            self._GPIO_PATH, 'gpio{}'.format(gpioId), self._EDGE)
        self._write(path, edge)

    def getPinEdge(self, pin):
        gpioId = self._getGpioId(pin)
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId),
                            self._EDGE)
        return self._readPin(path)

    def setPinValue(self, pin, value):
        gpioId = self._getGpioId(pin)
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId),
                            self._VALUE)
        self._write(path, value)

    def getPinValue(self, pin):
        gpioId = self._getGpioId(pin)
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId),
                            self._VALUE)
        return self._readPin(path)
