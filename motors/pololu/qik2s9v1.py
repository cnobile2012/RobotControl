#
# motors/pololu/qik2s9v1.py
#
# Usual device on Linux: /dev/ttyUSB0
#

"""
This code was written to work with the Pololu Qik 2s9v1 motor controller.
http://www.pololu.com/catalog/product/1110

by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .qik import Qik

__version__ = '1.0.0'
__version_info__ = tuple([ int(num) for num in __version__.split('.')])


class Qik2s9v1(Qik):
    QIK_VER_1 = 1
    QIK_VER_2 = 2
    _DEFAULT_DEVICE_ID = 0x09
    _COMMAND = {
        'get-fw-version': 0x01,
        'get-error': 0x02,
        'get-config': 0x03,
        'set-config': 0x04,
        'm0-coast': 0x06,
        'm1-coast': 0x07,
        'm0-forward-7bit': 0x08,
        'm0-forward-8bit': 0x09,
        'm0-reverse-7bit': 0x0A,
        'm0-reverse-8bit': 0x0B,
        'm1-forward-7bit': 0x0C,
        'm1-forward-8bit': 0x0D,
        'm1-reverse-7bit': 0x0E,
        'm1-reverse-8bit': 0x0F,
       }
    _ERRORS = {
        0: 'OK',
        1: 'Bit 0 Unused',
        2: 'Bit 1 Unused',
        4: 'Bit 2 Unused',
        8: 'Data Overrun Error',
        16: 'Frame Error',
        32: 'CRC Error',
        64: 'Format Error',
        128: 'Timeout',
        }
    DEVICE_ID = 0x00
    PWM_PARAM = 0x01
    MOTOR_ERR_SHUTDOWN = 0x02
    SERIAL_TIMEOUT = 0x03
    _CONFIG_NUM = {
        DEVICE_ID: 'Device ID',
        PWM_PARAM: 'PWM Parameter',
        MOTOR_ERR_SHUTDOWN: 'Shutdown Motors on Error',
        SERIAL_TIMEOUT: 'Serial Error',
        }
    _CONFIG_PWM = {
        0: (31500, '7-Bit, PWM Frequency 31.5kHz'),
        1: (15700, '8-Bit, PWM Frequency 15.7 kHz'),
        2: (7800, '7-Bit, PWM Frequency 7.8 kHz'),
        3: (3900, '8-Bit, PWM Frequency 3.9 kHz'),
        }
    _CONFIG_PWM_TO_VALUE = dict([(v[0], k) for k, v in _CONFIG_PWM.items()])
    MOTORS_CONTINUE = 0
    MOTORS_STOPPED = 1
    _CONFIG_MOTOR = {
        MOTORS_CONTINUE: 'Motors are not stopped on error.',
        MOTORS_STOPPED: 'Motors are stopped on error.',
        }

    def __init__(self, device, baud=38400, version=QIK_VER_2,
                 readTimeout=None, writeTimeout=None):
        super(Qik2s9v1, self).__init__(device, baud, version, readTimeout,
                                       writeTimeout)
        self._timeoutToValue = self._genTimeoutList(0.262)

    def getFirmwareVersion(self, device=_DEFAULT_DEVICE_ID):
        return self._getFirmwareVersion(device)

    def getError(self, device=_DEFAULT_DEVICE_ID, message=True):
        return self._getError(device, message)

    def getDeviceID(self, device=_DEFAULT_DEVICE_ID):
        return self._getDeviceID(device)

    def getPWMFrequency(self, device=_DEFAULT_DEVICE_ID, message=True):
        return self._getPWMFrequency(device, message)

    def getMotorShutdown(self, device=_DEFAULT_DEVICE_ID):
        return self._getMotorShutdown(device)

    def getSerialTimeout(self, device=_DEFAULT_DEVICE_ID):
        return self._getSerialTimeout(device)

    def setDeviceID(self, value, message=True):
        return self._setDeviceID(value, message)

    def setPWMFrequency(self, pwm, device=_DEFAULT_DEVICE_ID, message=True):
        return self._setPWMFrequency(pwm, device, message)

    def setMotorShutdown(self, value, device=_DEFAULT_DEVICE_ID, message=True):
        return self._setMotorShutdown(value, device, message)

    def setSerialTimeout(self, timeout, device=_DEFAULT_DEVICE_ID,
                         message=True):
        return self._setSerialTimeout(self, timeout, device, message)

    def setM0Coast(self, device=_DEFAULT_DEVICE_ID):
        self._setM0Coast(device)

    def setM1Coast(self, device=_DEFAULT_DEVICE_ID):
        self._setM1Coast(device)

    def setM0Speed(self, speed, device=_DEFAULT_DEVICE_ID):
        self._setM0Speed(speed, device)

    def setM1Speed(self, speed, device=_DEFAULT_DEVICE_ID):
        self._setM1Speed(speed, device)
