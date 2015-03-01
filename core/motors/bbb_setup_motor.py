#
# core/motors/bbb_setup_motor.py
#

import sys
import logging

from core.utils import ConfigLogger, getBasePath, isRootUser

log = ConfigLogger(getBasePath()).config('motors', level=logging.DEBUG)

if not isRootUser(): sys.exit(1)

from Adafruit_BBIO.UART import UART


# Available UARTs (UART1, UART2, UART4)

def setupUART(uart='UART4'):
    UART.setup(uart)
