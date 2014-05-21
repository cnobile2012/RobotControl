#
# central/utils/containers.py
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


from .gpio import BaseGPIO
from .events import Event


class BaseContainer(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Pin(BaseGPIO, BaseContainer):

    __trigger__ = Event.EDGE

    def __init__(self, pin, logger=None, level=logging.DEBUG):
        super(Pin, self).__init__(logger=logger, level=level)
        self._pin = pin
        self._gpioId = self._getGpioId(pin)
        self._fd = self._open()
        self._direction = ""
        self._edge = ""

    def _open(self):
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
        return self._fd and False or True

    def fileno(self):
        return self._fd

    @property
    def direction(self):
        if not self._direction:
            path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(self._gpioId),
                                self._DIRECTION)
            self._direction = self._readPin(path)

        return self._direction

    @property
    def edge(self):
        if not self._edge:
            path = os.path.join(self._GPIO_PATH, 'gpio{}'.format(self._gpioId),
                                self._EDGE)
            self._edge = self._readPin(path)

        return self._edge
