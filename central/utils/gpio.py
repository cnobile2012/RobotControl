#
# central/utils/gpio.py
#

"""
by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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

    def __init__(self, logger=None, level=logging.INFO):
        super(GPIO, self).__init__(logger=logger, level=level)

    def setMode(self, pin, direction=None, edge=None):
        """
        Sets digital pin mode. If previously not exported this method shall
        return 'True' else if already exported the return value shall be
        'False' unless either or both direction or edge is passed in, in which
        case the return value shall be 'True' if no exception is raised.

        pin       -- Any of the pin designation types. ex. GPIO1_1, GPIO_33, or
                     P8_24.
        direction -- Sets the pin to either input (GPIO.IN) or output (GPIO.OUT)
                     is default.
        edge      -- Sets the pin trigger edge to GPIO.RISING, GPIO.FALLING, or
                     GPIO.BOTH.
        """
        self._log.debug("pin: %s, direction: %s, edge: %s",
                        pin, direction, edge)
        gpioId = self._getGpioId(pin)
        result = self._export(gpioId)

        if direction or edge:
            self._waitForFile()

        if direction:
            if direction not in (self.IN, self.OUT):
                raise InvalidDirectionException(pin)

            path = os.path.join(
                self._GPIO_PATH, 'gpio{}'.format(gpioId), self._DIRECTION)
            self._writePin(path, direction)
            result = True

        if edge:
            if edge not in (self.RISING, self.FALLING, self.BOTH):
                raise InvalidEdgeException(pin)

            path = os.path.join(
                self._GPIO_PATH, 'gpio{}'.format(gpioId), self._EDGE)
            self._writePin(path, edge)
            result = True

        return result

    def cleanup(self, pin=None):
        result = False

        if pin is not None:
            gpioId = self._getGpioId(pin)
            result = self._unexport(gpioId)
        elif any([self._unexport(gpioId) for gpioId in self._findActivePins()]):
            result = True

        return result

    def setDirection(self, pin, direction):
        gpioId = self._getGpioId(pin)
        path = os.path.join(
            self._GPIO_PATH, 'gpio{}'.format(gpioId), self._DIRECTION)
        self._writePin(path, direction)

    def getDirection(self, pin):
        gpioId = self._getGpioId(pin)
        path = os.path.join(
            self._GPIO_PATH, 'gpio{}'.format(gpioId), self._DIRECTION)
        return self._readPin(path)

    def setEdge(self, pin, edge):
        gpioId = self._getGpioId(pin)
        path = os.path.join(
            self._GPIO_PATH, 'gpio{}'.format(gpioId), self._EDGE)
        self._writePin(path, edge)

    def getEdge(self, pin):
        gpioId = self._getGpioId(pin)
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId),
                            self._EDGE)
        return self._readPin(path)

    def setValue(self, pin, value):
        gpioId = self._getGpioId(pin)
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId),
                            self._VALUE)
        self._writePin(path, value)

    def getValue(self, pin):
        gpioId = self._getGpioId(pin)
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId),
                            self._VALUE)
        return int(self._readPin(path))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
