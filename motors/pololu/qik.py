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
__docformat__ = "restructuredtext en"


import serial


class Qik(object):
    _BAUD_DETECT = 0xAA
    _CONFIG_RETURN = {
        0: 'OK',
        1: 'Invalid Parameter',
        2: 'Invalid Value',
        }
    _BOOL_TO_INT = {False: 0, True: 1}

    def __init__(self, device, baud, version, readTimeout, writeTimeout, log):
        self._log = log
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
        self.currentPWM = {} # Default PWM

    def _genTimeoutList(self, const):
        """
        Generates a dict of the valid timeout values for the given `const`.
        The `const` value may change for different versions or types of
        Pololu boards.
        """
        result = {}

        for v in range(128):
            x = v & 0x0F
            y = (v >> 4) & 0x07

            if not y or (y and x > 7):
                result[const * x * 2**y] = v

        self._log and self._log.debug("Timeout list: %s", result)
        return result

    def findConnectedDevices(self):
        """
        """
        tmpTimeout = self._serial.timeout
        self._serial.timeout = 0.01

        for dev in range(128):
            device = self._getDeviceID(dev)

            if device is not None and int(device) not in self.currentPWM:
                num = self._getConfig(self.PWM_PARAM, device)
                self.currentPWM[int(device)] = num
                freq, msg = self._CONFIG_PWM.get(num, (None, None))
                self._log and self._log.info("Found device %s with PWM: %s",
                                             device, freq)

        self._serial.timeout = tmpTimeout

    def close(self):
        """
        Closes the serial connection.
        """
        if self._serial:
            self._serial.close()

    def isOpen(self):
        return self._serial.isOpen()

    def setCompactProtocol(self):
        """
        Set the compact protocol.
        """
        self._compact = True
        self._serial.write(bytes(self._BAUD_DETECT))
        self._log and self._log.debug("Compact protocol has been set.")

    def isCompactProtocol(self):
        return self._compact == True

    def setPololuProtocol(self):
        """
        Set the pololu protocol.
        """
        self._compact = False
        self._log and self._log.debug("Pololu protocol has been set.")

    def isPololuProtocol(self):
        return self._compact == False

    def _writeData(self, command, device, params=()):
        """
        Write the data to the device.

        :Parameters:
          command : `int`
            The command to write to the device.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          params : `tuple`
            Sequence of bytes to write.

        :Exceptions:
          SerialTimeoutException
            If the low level serial package times out.
          SerialException
            IO error when the port is not open.
        """
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
        self._log and self._log.debug("Wrote byte sequence: %s",
                                      [hex(num) for num in sequence])

    def _getFirmwareVersion(self, device):
        """
        Get the firmware version.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.

        :Returns:
          An integer indicating the version number.
        """
        cmd = self._COMMAND.get('get-fw-version')
        self._writeData(cmd, device)

        try:
            result = self._serial.read(size=1)
            result = int(result)
        except serial.SerialException as e:
            self._log and self._log.error("Error: %s", e, exc_info=True)
            raise e
        except ValueError as e:
            result = None

        return result

    def _getError(self, device, message):
        """
        Get the error message or value stored in the Qik hardware.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          message : `bool`
            If set to `True` a text message will be returned, if set to `False`
            the integer stored in the Qik will be returned.

        :Returns:
          A list of text messages, integers, or and empty list. See the
          `message` parameter above.
        """
        cmd = self._COMMAND.get('get-error')
        self._writeData(cmd, device)
        result = []
        bits = []

        try:
            num = self._serial.read(size=1)
            num = ord(num)
        except serial.SerialException as e:
            self._log and self._log.error("Error: %s", e, exc_info=True)
            raise e
        except TypeError as e:
            num = 0

        for i in range(7, -1, -1):
            bit = num & (1 << i)

            if bit:
                if message:
                    result.append(self._ERRORS.get(bit))
                else:
                    result.append(bit)

        return result

    def _getConfig(self, num, device):
        """
        Low level method used for all get config commands.

        :Parameters:
          num : `int`
            Number that indicates the config option to get from the hardware.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.

        :Returns:
          An integer representing the value stored in the hardware device.
        """
        cmd = self._COMMAND.get('get-config')
        self._writeData(cmd, device, params=(num,))

        try:
            result = self._serial.read(size=1)
            result = ord(result)
        except serial.SerialException as e:
            self._log and self._log.error("Error: %s", e, exc_info=True)
            raise e
        except TypeError as e:
            result = None

        return result

    def _getDeviceID(self, device):
        """
        Get the device ID.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.

        :Returns:
          An integer number of the hardware device ID.
        """
        return self._getConfig(self.DEVICE_ID, device)

    def _getPWMFrequency(self, device, message):
        """
        Get the PWM frequency stored on the hardware device.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          message : `bool`
            If set to `True` a text message will be returned, if set to `False`
            the integer stored in the Qik will be returned.

        :Returns:
          A text message or an int. See the `message` parameter above.
        """
        result = self._getConfig(self.PWM_PARAM, device)
        freq, msg = self._CONFIG_PWM.get(result, (result, 'Invalid Frequency'))

        if message:
            result = msg
        else:
            result = freq

        return result

    def _getMotorShutdown(self, device):
        """
        Get the motor shutdown on error status stored on the hardware device.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.

        :Returns:
          Text message indicating the status of the shutdown error.
        """
        result = self._getConfig(self.MOTOR_ERR_SHUTDOWN, device)
        return self._CONFIG_MOTOR.get(result, 'Unknown state')

    def _getSerialTimeout(self, device):
        """
        Get the serial timeout stored on the hardware device.

        Caution, more that one value returned from the Qik can have the same
        actual timeout value according the the formula below. I have verified
        this as an idiosyncrasy of the Qik itself. There are only a total of
        72 unique values that the Qik can logically use the remaining 56
        values are repeats of the 72.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.

        :Returns:
          The timeout value in seconds.
        """
        num = self._getConfig(self.SERIAL_TIMEOUT, device)

        if isinstance(num, int):
            x = num & 0x0F
            y = (num >> 4) & 0x07
            result = 0.262 * x * pow(2, y)
        else:
            result = num

        return result

    def _setConfig(self, num, value, device, message):
        """
        Low level method used for all set config commands.

        :Parameters:
          num : `int`
            Number that indicates the config option to get from the hardware.
          value : `int`
            The value to set in the hardware device.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          message : `bool`
            If set to `True` a text message will be returned, if set to `False`
            the integer stored in the Qik will be returned.

        :Returns:
          A text message or an int. See the `message` parameter above.

        :Exceptions:
          SerialException
            IO error indicating there was a problem reading from the serial
            connection.
        """
        cmd = self._COMMAND.get('set-config')
        self._writeData(cmd, device, params=(num, value, 0x55, 0x2A))

        try:
            result = self._serial.read(size=1)
            result = ord(result)
        except serial.SerialException as e:
            self._log and self._log.error("Error: %s", e, exc_info=True)
            raise e
        except TypeError as e:
            result = None

        if result is not None and message:
            result = self._CONFIG_RETURN.get(
                result, 'Unknown return value: {}'.format(result))

        return result

    def _setDeviceID(self, value, device, message):
        """
        Set the hardware device number. This is only needed if more that one
        device is on the same serial buss.

        :Parameters:
          value : `int`
            The device ID to set in the range of 0 - 127.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          message : `bool`
            If set to `True` a text message will be returned, if set to `False`
            the integer stored in the Qik will be returned.

        :Returns:
          A text message or an int. See the `message` parameter above.
        """
        result = self._setConfig(self.DEVICE_ID, value, device, message)

        # Try to keep the correct PWM for a Qik board.
        if value != device:
            num = self.currentPWM.pop(device)
        else:
            num = 0

        self.currentPWM[value] = num
        return result

    def _setPWMFrequency(self, pwm, device, message):
        """
        Set the PWM frequency.

        :Parameters:
          pwm : `int`
            The PWN frequency to set in hertz.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          message : `bool`
            If set to `True` a text message will be returned, if set to `False`
            the integer stored in the Qik will be returned.

        :Returns:
          A text message or an int. See the `message` parameter above.
        """
        value = self._CONFIG_PWM_TO_VALUE.get(pwm)

        if value is None:
            msg = "Invalid frequency: {}".format(pwm)
            self._log and self._log.error(msg)
            raise ValueError(msg)

        self.currentPWM[device] = value
        return self._setConfig(self.PWM_PARAM, value, device, message)

    def _setMotorShutdown(self, value, device, message):
        """
        Set the motor shutdown on error status stored on the hardware device.

        :Parameters:
          value : `int`
            An integer indicating the effect on the motors when an error occurs.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          message : `bool`
            If set to `True` a text message will be returned, if set to `False`
            the integer stored in the Qik will be returned.

        :Returns:
          Text message indicating the status of the shutdown error.
        """
        value = self._BOOL_TO_INT.get(value, 1)
        return self._setConfig(self.MOTOR_ERR_SHUTDOWN, value, device, message)

    def _setSerialTimeout(self, timeout, device, message):
        """
        Set the serial timeout on the hardware device.

        :Parameters:
          timeout : `float` or `int`
            The timeout value as defined by the hardware manual.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
          message : `bool`
            If set to `True` a text message will be returned, if set to `False`
            the integer stored in the Qik will be returned.

        :Returns:
          Text message indicating the status of the shutdown error.
        """
        keys = self._timeoutToValue.keys()
        keys.sort()
        timeout = min(keys, key=lambda x:abs(x-timeout))
        value = self._timeoutToValue.get(timeout, 0)
        return self._setConfig(self.SERIAL_TIMEOUT, value, device, message)

    def _setM0Coast(self, device):
        """
        Set motor 0 to coast.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
        """
        cmd = self._COMMAND.get('m0-coast')
        self._writeData(cmd, device)

    def _setM1Coast(self, device):
        """
        Set motor 1 to coast.

        :Parameters:
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
        """
        cmd = self._COMMAND.get('m1-coast')
        self._writeData(cmd, device)

    def _setM0Speed(self, speed, device):
        """
        Set motor 0 speed.

        :Parameters:
          speed : `int`
            Motor speed as an integer.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
        """
        self._setSpeed(speed, 'm0', device)

    def _setM1Speed(self, speed, device):
        """
        Set motor 1 speed.

        :Parameters:
          speed : `int`
            Motor speed as an integer.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
        """
        self._setSpeed(speed, 'm1', device)

    def _setSpeed(self, speed, motor, device):
        """
        Set motor speed. This method takes into consideration the PWM frequency
        that the hardware is currently running at and limits the values passed
        to the hardware accordingly.

        :Parameters:
          speed : `int`
            Motor speed as an integer.
          motor : `str`
            A string value indicating the motor to set the speed on.
          device : `int`
            The device is the integer number of the hardware devices ID and
            is only used with the Pololu Protocol.
        """
        reverse = False

        if speed < 0:
            speed = -speed
            reverse = True

        # 0 and 2 for Qik 2s9v1, 0, 2, and 4 for 2s12v10
        if self.currentPWM.get(device) in (0, 2, 4,) and speed > 127:
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
            msg = "Invalid motor specified: {}".format(motor)
            self._log and self._log.error(msg)
            raise ValueError(msg)

        self._writeData(cmd, device, params=(speed,))
