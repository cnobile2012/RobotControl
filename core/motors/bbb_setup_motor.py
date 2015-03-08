#
# core/motors/bbb_setup_motor.py
#

"""
The ConfigLogger class is used to configure loggers.

by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import logging

from core.utils import ConfigLogger, getBasePath, isRootUser

log = ConfigLogger(getBasePath()).config('motors', level=logging.DEBUG)

if not isRootUser(): sys.exit(1)

from Adafruit_BBIO.UART import UART


# Available UARTs (UART1, UART2, UART4)

def setupUART(uart='UART4'):
    UART.setup(uart)
