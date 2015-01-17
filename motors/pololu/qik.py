#
# motors/pololu/qik.py
#
# Usual device on Linux: /dev/ttyUSB0
#

"""
This code was written to work with the Pololu Qik motor controllers.

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
    _BAUD_DETECT = 0xAA
    _CONFIG_RETURN = {
        0: 'OK',
        1: 'Invalid Parameter',
        2: 'Invalid Value',
        }

    def __init__(self, device, baud, version, readTimeout, writeTimeout):
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
        self._currentPWM = 0 # Default PWM

    def _genTimeoutList(self, const):
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

    def _getFirmwareVersion(self, device):
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

    def _getError(self, device, message):
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

    def _getConfig(self, num, device):
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

    def _getDeviceID(self, device):
        return self._getConfig(self.DEVICE_ID, device)

    def _getPWMFrequency(self, device, message):
        result = self._getConfig(self.PWM_PARAM, device)
        freq, msg = self._CONFIG_PWM.get(result, (0, 'Invalid Frequency'))

        if message:
            result = msg
        else:
            result = freq

        return result

    def _getMotorShutdown(self, device):
        result = self._getConfig(self.MOTOR_ERR_SHUTDOWN, device)
        return self._CONFIG_MOTOR.get(result, 'Unknown state')

    def _getSerialTimeout(self, device):
        """
        Caution, more that one value returned from the Qik can have the same
        actual timeout value according the the formula below. I have verified
        this as a bug in the Qik itself. There are only a total of 72 unique
        values that the Qik can logically use the remaining 56 values are
        repeats of the 72.
        """
        result = self._getConfig(self.SERIAL_TIMEOUT, device)
        x = result & 0x0F
        y = (result >> 4) & 0x07
        return 0.262 * x * pow(2, y)

    def _setConfig(self, num, value, device, message):
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

    def _setDeviceID(self, value, message):
        return self._setConfig(self.DEVICE_ID, value, message)

    def _setPWMFrequency(self, pwm, device, message):
        value = self._CONFIG_PWM_TO_VALUE.get(pwm)

        if value is None:
            raise ValueError("Invalid frequency: {}".format(pwm))

        self._currentPWM = value
        return self._setConfig(self.PWM_PARAM, value, device, message)

    def _setMotorShutdown(self, value, device, message):
        if value not in self._CONFIG_MOTOR:
            raise ValueError(
                "Invalid motor shutdown on error value: {}".format(value))

        return self._setConfig(self.MOTOR_ERR_SHUTDOWN, value, device, message)

    def _setSerialTimeout(self, timeout, device, message):
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
        return self._setConfig(self.SERIAL_TIMEOUT, value, device, message)

    def _setM0Coast(self, device):
        cmd = self._COMMAND.get('m0-coast')
        self._sendProtocol(cmd, device)

    def _setM1Coast(self, device):
        cmd = self._COMMAND.get('m1-coast')
        self._sendProtocol(cmd, device)

    def _setM0Speed(self, speed, device):
        self._setSpeed(speed, 'm0', device)

    def _setM1Speed(self, speed, device):
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
