#
# motor_control.py
#

import sys
import logging

from utils import ConfigLogger, getBasePath, isRoot

log = ConfigLogger(getBasePath()).config('motor-control', level=logging.DEBUG)

if not isRoot(): exit(1)

from Adafruit_BBIO.SPI import SPI


