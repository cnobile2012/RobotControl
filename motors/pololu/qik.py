#
# motors/pololu/qik.py
#
# Usual device on Linux: /dev/ttyUSB0
#

"""
This code was written to work with the Pololu Qik motor controller.
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

import serial


class Qik(object):
    QIK_VER_1 = 1
    QIK_VER_2 = 2
    _BAUD_DETECT = 0xAA
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
    _CONFIG_RETURN = {
        0: 'OK',
        1: 'Invalid Parameter',
        2: 'Invalid Value',
        }

    def __init__(self, device, baud=38400, version=QIK_VER_2,
                 readTimeout=None, writeTimeout=None):
        self._version = version
        self._device_numbers = []
        self._serial = serial.Serial(port=device, baudrate=baud,
                                     bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=readTimeout,
                                     writeTimeout=writeTimeout)
        # DO NOT default to compact protocol. If your Qik gets bricked and
        # the default it compact it cannot be unbricked with this API.
        self.setPololuProtocol()
        self._timeoutToValue = self._genTimeoutList()
        self._currentPWM = 0 # 31500 7 bit mode

    def _genTimeoutList(self, const=0.262):
        result = {}

        for v in range(128):
            x = v & 0x0F
            y = (v >> 4) & 0x07

            if not y or (y and x > 7):
                #print bin(y), bin(x)
                result[const * x * 2**y] = v

        return result

    def close(self):
        if self._serial:
            self._serial.close()

    def setCompactProtocol(self):
        """
        Set the compact protocol, this is the default.
        """
        self._compact = True
        self._serial.write(bytes(self._BAUD_DETECT))

    def setPololuProtocol(self):
        """
        Set the pololu protocol.
        """
        self._compact = False

    def setDeviceNumbers(self, size, prefix, startNum=_DEFAULT_DEVICE_ID):
        self._device_numbers[:] = [
            ("{}{:03}".format(prefix, idx), num)
            for num, idx in enumerate(range(size), start=start_num)]

    def getDeviceNumber(self, key):
        dnMap = dict(self._device_numbers)
        return dnMap.get(key)

    def _sendProtocol(self, command, device, params=()):
        sequence = []

        if self._compact:
            sequence.append(command | 0x80)
        else:
            sequence.append(self._BAUD_DETECT)
            sequence.append(device)
            sequence.append(command)

        for param in params:
            sequence.append(param)

        self._serial.write(bytearray(sequence))

    def getFirmwareVersion(self, device=_DEFAULT_DEVICE_ID):
        cmd = self._COMMAND.get('get-fw-version')
        self._sendProtocol(cmd, device)

        try:
            result = self._serial.read(size=1)
            result = int(result)
        except serial.SerialException as e:
            print e
            raise e
        except ValueError as e:
            print e

        return result

    def getError(self, device=_DEFAULT_DEVICE_ID, message=True):
        """
        Returns '0 Unused' if there is no error to return.
        """
        cmd = self._COMMAND.get('get-error')
        self._sendProtocol(cmd, device)

        try:
            result = self._serial.read(size=1)
            result = ord(result)
        except serial.SerialException as e:
            print e
            raise e
        except TypeError as e:
            print e

        if message:
            result = self._ERRORS.get(result, result)

        return result

    def getConfig(self, num, device=_DEFAULT_DEVICE_ID):
        cmd = self._COMMAND.get('get-config')
        self._sendProtocol(cmd, device, params=(num,))

        try:
            result = self._serial.read(size=1)
            result = ord(result)
        except serial.SerialException as e:
            print e
            raise e
        except TypeError as e:
            print e

        return result

    def getDeviceID(self, device=_DEFAULT_DEVICE_ID):
        return self.getConfig(self.DEVICE_ID, device=device)

    def getPWMFrequency(self, device=_DEFAULT_DEVICE_ID, message=True):
        result = self.getConfig(self.PWM_PARAM, device=device)
        freq, msg = self._CONFIG_PWM.get(result, (0, 'Invalid Frequency'))

        if message:
            result = msg
        else:
            result = freq

        return result

    def getMotorShutdown(self, device=_DEFAULT_DEVICE_ID):
        result = self.getConfig(self.MOTOR_ERR_SHUTDOWN, device=device)
        return self._CONFIG_MOTOR.get(result, 'Unknown state')

    def getSerialTimeout(self, device=_DEFAULT_DEVICE_ID):
        """
        Caution, more that one value returned from theQik can have the same
        actual timeout value according the the formula below. I have verified
        this as a bug in the Qik itself. There are only a total of 72 unique
        values that the Qik can logicly use the remaining 56 values are repeats
        of the 72.
        """
        result = self.getConfig(self.SERIAL_TIMEOUT, device=device)
        x = result & 0x0F
        y = (result >> 4) & 0x07
        return 0.262 * x * pow(2, y)

    def setConfig(self, num, value, device=_DEFAULT_DEVICE_ID, message=True):
        cmd = self._COMMAND.get('set-config')
        self._sendProtocol(cmd, device, params=(num, value, 0x55, 0x2A))

        try:
            result = self._serial.read(size=1)
            result = ord(result)
        except serial.SerialException as e:
            print e
            raise e
        except TypeError as e:
            print e

        if message:
            result = self._CONFIG_RETURN.get(
                result, 'Unknown return value: {}'.format(result))

        return result

    def setDeviceID(self, value, message=True):
        return self.setConfig(self.DEVICE_ID, value, message=message)

    def setPWMFrequency(self, pwm, device=_DEFAULT_DEVICE_ID, message=True):
        value = self._CONFIG_PWM_TO_VALUE.get(pwm)

        if value is None:
            raise ValueError("Invalid frequency: {}".format(pwm))

        self._currentPWM = value
        return self.setConfig(self.PWM_PARAM, value, device=device,
                              message=message)

    def setMotorShutdown(self, value, device=_DEFAULT_DEVICE_ID, message=True):
        if value not in self._CONFIG_MOTOR:
            raise ValueError(
                "Invalid motor shutdown on error value: {}".format(value))

        return self.setConfig(self.MOTOR_ERR_SHUTDOWN, value, device=device,
                              message=message)

    def setSerialTimeout(self, timeout, device=_DEFAULT_DEVICE_ID,
                         message=True):
        """
        Setting the serial timeout to anything other than zero will cause an
        error if the serial line is inactive for the time set. This may not be
        a good thing as leaving the Qik idle may be a required event. Why
        would you want the Qik to report an error when none actually occurred
        and your Qik was just idle?

        This also explains why if the Qik is set at a very low timeout that the
        red LED will come on almost immediately. You will not even get a chance
        to send it a command before the timeout. This would be like bricking
        your Qik. Not a good thing.

        OK, so how do we actually use the serial timeout. Good question, the
        best way I can think of is to send the Qik a keep alive signal. One
        way of doing this is to execute the getError() method at a little less
        than half the timeout period. So if the timeout was set to 200ms you
        would get the error status every 90ms. The Qik will stay alive unless
        the keep alive signal is not seen. This should solve the problem, but
        getting the timing right may be an issue as different Qiks will timeout
        a little differently from others. When using more than one Qik on the
        serial buss this may become an issue. You will need to play with some
        different values.
        """
        keys = self._timeoutToValue.keys()
        keys.sort()
        timeout = min(keys, key=lambda x:abs(x-timeout))
        value = self._timeoutToValue.get(timeout, 0)
        return self.setConfig(self.SERIAL_TIMEOUT, value, device=device,
                              message=message)

    def setM0Coast(self, device=_DEFAULT_DEVICE_ID):
        cmd = self._COMMAND.get('m0-coast')
        self._sendProtocol(cmd, device)

    def setM1Coast(self, device=_DEFAULT_DEVICE_ID):
        cmd = self._COMMAND.get('m1-coast')
        self._sendProtocol(cmd, device)

    def setM0Speed(self, speed, device=_DEFAULT_DEVICE_ID):
        self._setSpeed(speed, 'm0', device)

    def setM1Speed(self, speed, device=_DEFAULT_DEVICE_ID):
        self._setSpeed(speed, 'm1', device)

    def _setSpeed(self, speed, motor, device):
        reverse = False

        if speed < 0:
            speed = -speed
            reverse = True

        # 0 and 2 for Qik 2s9v1, 0, 2, and 4 for 2s12v10
        if self._currentPWM in (0, 2, 4,) and speed > 127:
            speed = 127

        if speed > 127:
            if speed > 255:
                speed = 255

            if reverse:
                cmd = self._COMMAND.get('{}-reverse-8bit'.format(motor))
            else:
                cmd = self._COMMAND.get('{}-forward-8bit'.format(motor))

            speed -= 128
        else:
            if reverse:
                cmd = self._COMMAND.get('{}-reverse-7bit'.format(motor))
            else:
                cmd = self._COMMAND.get('{}-forward-7bit'.format(motor))

        if not cmd:
            raise ValueError("Invalid motor specified: {}".format(motor))

        self._sendProtocol(cmd, device, params=(speed,))
