#
# central/utils/__init__.py
#

"""
The functions and classes here are utilities and can be used anywhere in
the application.

by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import logging

from .logging_config import getBasePath, ConfigLogger

from .exceptions import *
from .gpio import GPIO


def isRootUser(logger=''):
    result = True
    log = logging.getLogger(logger)

    if os.getuid() != 0:
        result = False
        log.critical("You must be root to run this application, found user: %s",
                     os.environ.get('LOGNAME'))

    return result


def setupMultiplePins(pinHeader, startPin, pinRange=8, direction=GPIO.OUT):
    """
    Sets up a range of pins to a specified direction. (GPIO.IN or GPIO.OUT)
    """
    validHeaders = (8, 9)
    validDir = (GPIO.IN, GPIO.OUT)

    if pinHeader not in validHeaders:
        raise TypeError("Invalid header number {} must be one of {}.".format(
            pinHeader, validHeaders))

    if direction not in validDir:
        raise TypeError("Invalid pin direction {} must be one of {}.".format(
            direction, validDir))

    for idx in range(pinRange):
        pin = startPin + idx
        channel = "P{}_{}".format(pinHeader, pin)
        #print channel, direction
        GPIO.setup(channel, direction)


__all__ = ['isRootUser', 'GPIO', 'getBasePath', 'ConfigLogger',
           'setupMultiplePins',
           'InvalidPinNomenclatureException', 'InvalidDirectionException',
           'InvalidEdgeException', 'InvalidArgumentsException']
