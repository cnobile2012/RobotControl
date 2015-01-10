#
# motors/pololu/qik.py
#
# Usual device on Linux: /dev/ttyUSB0
#

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
        0: '0 Unused',
        1: '1 Unused',
        2: '2 Unused',
        4: 'Data Overrun Error',
        4: 'Frame Error',
        5: 'CRC Error',
        6: 'Format Error',
        7: 'Timeout',
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
    PWM_7B_31500 = 0
    PWM_8B_15700 = 1
    PWM_7B_7800 = 2
    PWM_8B_3900 = 3
    _CONFIG_PWM = {
        PWM_7B_31500: (31500, '7-Bit, PWM Frequency 31.5kHz'),
        PWM_8B_15700: (15700, '8-Bit, PWM Frequency 15.7 kHz'),
        PWM_7B_7800: (7800, '7-Bit, PWM Frequency 7.8 kHz'),
        PWM_8B_3900: (3900, '8-Bit, PWM Frequency 3.9 kHz'),
        }
    _CONFIG_PWN_TO_VALUE = [(v[0], k) for k, v in _CONFIG_PWM.items()]
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
        self.compactProtocol()

    def close(self):
        if self._serial:
            self._serial.close()

    def compactProtocol(self):
        """
        Set the compact protocol, this is the default.
        """
        self._compact = True
        self._serial.write(bytes(self._BAUD_DETECT))

    def pololuProtocol(self):
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
            result = self._ERRORS.get(result)

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

    def setPWMFrequency(self, value, device=_DEFAULT_DEVICE_ID, message=True):
        num = self._CONFIG_PWN_TO_VALUE.get(value)

        if not num:
            raise ValueError("Invalid frequency: {}".format(value))

        return self.setConfig(self.PWM_PARAM, num, device=device,
                              message=message)

    def setMotorShutdown(self, value, device=_DEFAULT_DEVICE_ID, message=True):
        if value not in self._CONFIG_MOTOR:
            raise ValueError(
                "Invalid motor shutdown on error value: {}".format(value))

        return self.setConfig(self.MOTOR_ERR_SHUTDOWN, value, device=device,
                              message=message)

    def setSerialTimeout(self, value, device=_DEFAULT_DEVICE_ID, message=True):
        #if isinstance(value, str) and value.isdigit():
        #    value = int(value)
        #elif not isinstance(value, int):
        #    raise ValueError("Invalid serial timeout value: {}".format(value))

        #value = value / 0.262


        return self.setConfig(self.SERIAL_TIMEOUT, value, device=device,
                              message=message)

    def setM0Coast(self, device=_DEFAULT_DEVICE_ID):
        cmd = self._COMMAND.get('m0-coast')
        self._sendProtocol(cmd, device)

    def setM1Coast(self, device=_DEFAULT_DEVICE_ID):
        cmd = self._COMMAND.get('m1-coast')
        self._sendProtocol(cmd, device)

    def setM0Speed(self, speed, device=_DEFAULT_DEVICE_ID):
        self._setSpeed(speed, 'm0', device=device)

    def setM1Speed(self, speed, device=_DEFAULT_DEVICE_ID):
        self._setSpeed(speed, 'm1', device=device)

    def _setSpeed(self, speed, motor, device):
        reverse = False

        if speed < 0:
            speed = -speed
            reverse = True

        if speed > 255:
            speed = 255

        if speed > 127:
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
