#
# central/utils/basegpio.py
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

import re, os
import time, logging

from .logging_config import getBasePath, ConfigLogger
from .exceptions import (
    InvalidPinNomenclatureException, InvalidArgumentsException)


class OpenCM(object):
    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        return self.fd

    def __exit__(self, type, value, traceback):
        os.close(self.fd)


class BaseGPIO(object):
    __DIRS_RE = re.compile(r'^gpio\d{1,3}$')
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
        80, 81, 86, 87, 88, 89, 115, 117, 120, 121, 122, 123)
    _GPIO_PATH = '/sys/class/gpio'
    _ACTIVE_LOW = 'active_low'
    _DIRECTION = 'direction'
    _EDGE = 'edge'
    _UEVENT = 'uevent'
    _VALUE = 'value'

    def __init__(self, logger=None, level=logging.INFO):
        if not logger:
            ConfigLogger().config(level=level)
            logger = ''

        self._log = logging.getLogger(logger)
        self._log.setLevel(level)

    def isRootUser(self):
        return os.getuid() == 0

    def _findActivePins(self):
        dirs = os.listdir(self._GPIO_PATH)
        dirs = [f for f in dirs
                if os.path.isdir(os.path.join(self._GPIO_PATH, f))]
        self._log.debug("dirs: %s", dirs)
        return [d[4:] for d in dirs if self.__DIRS_RE.search(d)]

    def _waitForFile(self, timeout=0.5):
        if not self.isRootUser():
            time.sleep(timeout)

    def _export(self, gpioId):
        result = False
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId))

        if not os.path.exists(path):
            path = os.path.join(self._GPIO_PATH, self.__EXPORT)
            self._writePin(path, gpioId)
            result = True

        self._log.debug("result: %s, path: %s", result, path)
        return result

    def _unexport(self, gpioId):
        result = False
        path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(gpioId))

        if os.path.exists(path):
            path = os.path.join(self._GPIO_PATH, self.__UNEXPORT)
            self._writePin(path, gpioId)
            result = True

        self._log.debug("result: %s, path: %s", result, path)
        return result

    def _getGpioId(self, pin):
        result = 0
        self._log.debug("pin: %s", pin)

        if not isinstance(pin, basestring):
            raise InvalidPinNomenclatureException(pin)

        pin = pin.count('.') == 1 and pin.replace('.', '_') or pin
        head, delimiter, tail = pin.partition('_')
        head = head.upper()

        if (len(head) == 2 and head[0] == 'P' and
            head[-1].isdigit() and tail.isdigit()):
            result = self.__PIN_MAP.get(int(head[-1]), {}).get(int(tail), 0)
        elif head == 'GPIO' and tail.isdigit():
            result = int(tail)
        elif (len(head) == 5 and head[:4] == 'GPIO' and
              head[-1].isdigit() and tail.isdigit()):
            result = int(head[-1]) * 32 + int(tail)
        else:
            raise InvalidPinNomenclatureException(pin)

        if result not in self.__VALID_PINS:
            raise InvalidPinNomenclatureException(pin)

        self._log.debug("result: %s", result)
        return result

    def _readPin(self, path, bytes=128):
        with OpenCM(os.open(path, os.O_RDONLY)) as fd:
            result = os.read(fd, bytes)
            result = result.strip()
            self._log.debug("Read path '%s' and returned value '%s'.",
                            path, result)

        return result

    def _writePin(self, path, value):
        value = str(value)

        with OpenCM(os.open(path, os.O_WRONLY)) as fd:
            numBytes = os.write(fd, value)
            self._log.debug("Wrote to path '%s' value '%s'.", path, value)

            if numBytes != len(value):
                raise IOError("Wrong number of bytes witten to {}, wrote: {}, "
                              "should have been: {}".format(
                                  path, numBytes, len(value)))

    def _openPin(self, path):
        return os.open(path, os.O_RDONLY)
