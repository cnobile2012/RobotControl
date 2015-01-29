#!/usr/bin/env python
#
# motors/pololu/test_qik2s9v1.py
#

import os
import unittest
import time
import logging

from motors.pololu import Qik2s9v1


BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         '..', '..', '..', 'logs'))

def setupLogger(fullpath=None, level=logging.DEBUG):
    FORMAT = ("%(asctime)s %(levelname)s %(module)s %(funcName)s "
              "[line:%(lineno)d] %(message)s")
    logging.basicConfig(filename=fullpath, format=FORMAT, level=level)
    return logging.getLogger()


class TestQik2s9v1(unittest.TestCase):
    """
    Unit tests for the Qik 2s9v1 motor controller.

    Most tests have a for loop which first tests the pololu protocol then tests
    the compact protocol.
    """
    _DEFAULT_TTY = '/dev/ttyUSB0'
    _PORTOCOL_MAP = {0: "Pololu Protocol", 1: "Compact Protocol"}

    def __init__(self, name):
        super(TestQik2s9v1, self).__init__(name)
        # Timeouts [(0.0, 0), (0.262, 1), ...]
        self._timeoutMap = dict(self.genTimeoutList())
        logFilePath = os.path.join(BASE_PATH, 'pololu_qik2s9v1.log')
        self._log = setupLogger(fullpath=logFilePath)

    def genTimeoutList(self, const=0.262):
        result = []

        for v in range(128):
            x = v & 0x0F
            y = (v >> 4) & 0x07

            if not y or (y and x > 7):
                result.append((v, const * x * 2**y))

        return result

    def setUp(self):
        self._log.debug("Processing")
        self._qik = Qik2s9v1(self._DEFAULT_TTY, readTimeout=5, log=self._log)

    def tearDown(self):
        self._log.debug("Processing")

        if self._qik.isOpen():
            for d in self._qik.currentPWM:
                self._qik.setDeviceID(self._qik.DEFAULT_DEVICE_ID, device=d)

            self._qik.getError()
            self._qik.setPWMFrequency(31500)
            self._qik.setMotorShutdown(True)
            self._qik.setSerialTimeout(0.0)
            self._qik.setM0Speed(0)
            self._qik.setM0Coast()
            self._qik.setM1Speed(0)
            self._qik.setM1Coast()
            self._qik.close()
            self._qik = None

    def test_close(self):
        self._log.debug("Processing")
        self.assertTrue(self._qik.isOpen() == True)
        self._qik.close()
        self.assertTrue(self._qik.isOpen() == False)

    def test_setCompactProtocol(self):
        """
        The compact protocol is not the default.
        """
        self._log.debug("Processing")
        self.assertTrue(self._qik.isCompactProtocol() == False)
        self._qik.setCompactProtocol()
        self.assertTrue(self._qik.isCompactProtocol() == True)

    def test_setPololuProtocol(self):
        """
        The pololu portocol is the default.
        """
        self._log.debug("Processing")
        self.assertTrue(self._qik.isPololuProtocol() == True)
        self._qik.setCompactProtocol()
        self.assertTrue(self._qik.isPololuProtocol() == False)

    def test_getFirmwareVersion(self):
        self._log.debug("Processing")
        self.assertTrue(self._qik.getFirmwareVersion() in (1, 2))
        self._qik.setCompactProtocol()
        self.assertTrue(self._qik.getFirmwareVersion() in (1, 2))

    # Test for Data Overrun Error

    # Test for Frame Error

    # Test for CRC Error

    def test_getError_FormatError(self):
        self._log.debug("Processing")
        command = 0x70 # Bad command breaks in both protocols
        num = 64
        error = self._qik._ERRORS.get(num)

        for i in range(2):
            self._qik._writeData(command, self._qik.DEFAULT_DEVICE_ID)
            result = self._qik.getError(message=False)
            msg = "{}: Invalid error '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, [num])
            self.assertTrue(num in result and len(result) == 1, msg=msg)
            self._qik._writeData(command, self._qik.DEFAULT_DEVICE_ID)
            result = self._qik.getError()
            msg = "{}: Invalid error '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, [error])
            self.assertTrue(error in result and len(result) == 1, msg=msg)
            self._qik.setCompactProtocol()

    def test_getError_TimeoutError(self):
        self._log.debug("Processing")
        timeout = 0.262
        num = 128
        error = self._qik._ERRORS.get(num)

        for i in range(2):
            self._qik.setSerialTimeout(timeout)
            time.sleep(0.275)
            result = self._qik.getError(message=False)
            msg = "{}: Invalid error '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, [num])
            self.assertTrue(num in result and len(result) == 1, msg=msg)
            self._qik.setSerialTimeout(timeout)
            time.sleep(0.275)
            result = self._qik.getError()
            msg = "{}: Invalid error '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, [error])
            self.assertTrue(error in result and len(result) == 1, msg=msg)
            self._qik.setCompactProtocol()

    #@unittest.skip("Temporarily skipped")
    def test_getDeviceID(self):
        """
        Only test Pololu protocol, it's the only protocol that uses the device
        ID.
        """
        self._log.debug("Processing")
        devices = (self._qik.DEFAULT_DEVICE_ID, 127)
        # Default device
        result = self._qik.getDeviceID(device=devices[0])
        msg = "Invalid device '{}' should be '{}'.".format(
            self._PORTOCOL_MAP.get(0), result, devices[0])
        self.assertTrue(result == devices[0], msg=msg)
        # Reset device
        self._qik.setDeviceID(devices[1], device=devices[0])
        result = self._qik.getDeviceID(device=devices[1])
        msg = "{}: Invalid device '{}' should be '{}'.".format(
            self._PORTOCOL_MAP.get(0), result, devices[1])
        self.assertTrue(result == devices[1], msg=msg)

    def test_getPWMFrequency(self):
        self._log.debug("Processing")

        for i in range(2):
            result = self._qik.getPWMFrequency()
            msg = "{}: Invalid PWM frequency '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result,
                self._qik._CONFIG_PWM.get(0)[1])
            self.assertTrue(result == self._qik._CONFIG_PWM.get(0)[1], msg=msg)
            result = self._qik.getPWMFrequency(message=False)
            msg = "{}: Invalid PWM frequency '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result,
                self._qik._CONFIG_PWM.get(0)[0])
            self.assertTrue(result == self._qik._CONFIG_PWM.get(0)[0], msg=msg)
            self._qik.setCompactProtocol()

    def test_getMotorShutdown(self):
        self._log.debug("Processing")

        for i in range(2):
            result = self._qik.getMotorShutdown()
            msg = ("{}: Invalid motor shutdown value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result,
                            self._qik._CONFIG_MOTOR.get(True))
            self.assertTrue(result == self._qik._CONFIG_MOTOR.get(True),
                            msg=msg)
            self._qik.setCompactProtocol()

    def test_getSerialTimeout(self):
        self._log.debug("Processing")

        for i in range(2):
            result = self._qik.getSerialTimeout()
            msg = ("{}: Invalid serial timeout value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result,
                            self._timeoutMap.get(0))
            self.assertTrue(result == self._timeoutMap.get(0), msg=msg)
            self._qik.setSerialTimeout(200.0)
            result = self._qik.getSerialTimeout()
            msg = ("{}: Invalid serial timeout value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result,
                            self._timeoutMap.get(108))
            self.assertTrue(result == self._timeoutMap.get(108), msg=msg)
            self._qik.setCompactProtocol()
            self._qik.setSerialTimeout(0.0)

    def test_setDeviceID(self):
        self._log.debug("Processing")
        devices = (self._qik.DEFAULT_DEVICE_ID, 127)

        for i in range(2):
            result = self._qik.setDeviceID(devices[1], devices[0])
            msg = ("{}: Invalid device ID '{}' should be '{}'.").format(
                self._PORTOCOL_MAP.get(i), result, 'OK')
            self.assertTrue(result == 'OK', msg=msg)
            result = self._qik.setDeviceID(devices[0], devices[1],
                                           message=False)
            msg = ("{}: Invalid device ID '{}' should be '{}'.").format(
                self._PORTOCOL_MAP.get(i), result, devices[0])
            self.assertTrue(result == 0, msg=msg)
            self._qik.setCompactProtocol()

    def test_setPWMFrequency(self):
        self._log.debug("Processing")
        pwms = [v[0] for v in self._qik._CONFIG_PWM.values()]
        nums = dict([(v[0], k) for k, v in self._qik._CONFIG_PWM.items()])

        for i in range(2):
            for pwm in pwms:
                result = self._qik.setPWMFrequency(pwm)
                rtn = self._qik._CONFIG_RETURN.get(0)
                msg = ("{}: Invalid PM return text '{}' should be '{}'."
                       ).format(self._PORTOCOL_MAP.get(i), result, rtn)
                self.assertTrue(result == rtn, msg=msg)
                result = self._qik.setPWMFrequency(pwm, message=False)
                msg = ("{}: Invalid PWM return value '{}' should be '{}'."
                       ).format(self._PORTOCOL_MAP.get(i), result, 0)
                self.assertTrue(result == 0, msg=msg)

            self._qik.setCompactProtocol()

    def test_setMotorShutdown(self):
        self._log.debug("Processing")
        command = 0x70 # Bad command breaks in both protocols
        error = self._qik._ERRORS.get(64) # Format error
        rtn = self._qik._CONFIG_RETURN.get(0)

        for i in range(2):
            # Start with default motor stop on errors
            sdValue = self._qik._CONFIG_MOTOR.get(True)
            # Start up motor M0
            self._qik.setM0Speed(50)
            result = self._qik.getMotorShutdown()
            msg = ("{}: Invalid motor shutdown value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, sdValue)
            self.assertTrue(result == sdValue, msg=msg)
            time.sleep(0.5)
            # Create an error condition that will stop the motors.
            self._qik._writeData(command, self._qik.DEFAULT_DEVICE_ID)
            result = self._qik.getError()
            msg = ("{}: Invalid response error text '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, [error])
            self.assertTrue(error in result and len(result) == 1, msg=msg)

            # Switch to non-stopping motors
            sdValue = self._qik._CONFIG_MOTOR.get(False)
            result = self._qik.setMotorShutdown(False)
            msg = "{}: Invalid response '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, rtn)
            self.assertTrue(result == rtn, msg=msg)
            result = self._qik.getMotorShutdown()
            msg = ("{}: Invalid motor shutdown value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, sdValue)
            self.assertTrue(result == sdValue, msg=msg)
            # Start up motor M0, If change motor shutdown need to come to
            # full stop.
            self._qik.setM0Speed(0)
            self._qik.setM0Speed(-50)
            result = self._qik.getMotorShutdown()
            msg = ("{}: Invalid motor shutdown value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, sdValue)
            self.assertTrue(result == sdValue, msg=msg)
            time.sleep(0.5)
            # Create an error condition that will not stop the motors.
            self._qik._writeData(command, self._qik.DEFAULT_DEVICE_ID)
            result = self._qik.getError()
            msg = ("{}: Invalid response error text '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, [error])
            self.assertTrue(error in result and len(result) == 1, msg=msg)
            self._qik.setM0Speed(0)
            self._qik.setM0Coast()

            # Switch back to stopping motor.
            result = self._qik.setMotorShutdown(True)
            msg = "{}: Invalid response '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, rtn)
            self.assertTrue(result == rtn, msg=msg)
            self._qik.setCompactProtocol()

    def test_setSerialTimeout(self):
        self._log.debug("Processing")
        rtn = self._qik._CONFIG_RETURN.get(0)
        shortDelay = self._timeoutMap.get(1)
        longDelay = self._timeoutMap.get(127)

        for i in range(2):
            # Test short timeout, will be 0.262 on the Qik
            result = self._qik.setSerialTimeout(0.3)
            msg = ("{}: Invalid serial timeout '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, rtn)
            self.assertTrue(result == rtn, msg=msg)
            result = self._qik.getSerialTimeout()
            msg = ("{}: Invalid serial timeout value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, shortDelay)
            self.assertTrue(result == shortDelay, msg=msg)
            # Test long timeout, will be 503.04 on the Qik
            result = self._qik.setSerialTimeout(500.0)
            msg = ("{}: Invalid serial timeout '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, rtn)
            self.assertTrue(result == rtn, msg=msg)
            result = self._qik.getSerialTimeout()
            msg = ("{}: Invalid serial timeout value '{}' should be '{}'."
                   ).format(self._PORTOCOL_MAP.get(i), result, longDelay)
            self.assertTrue(result == longDelay, msg=msg)
            self._qik.setCompactProtocol()

    @unittest.skip("Skipped, no return values.")
    def test_setM0Coast(self):
        self._log.debug("Processing")

        for i in range(2):
            self._qik.setM0Speed(50)
            time.sleep(0.5)
            self._qik.setM0Coast()

    @unittest.skip("Skipped, no return values.")
    def test_setM1Coast(self):
        self._log.debug("Processing")

        for i in range(2):
            self._qik.setM1Speed(50)
            time.sleep(0.5)
            self._qik.setM1Coast()

    @unittest.skip("Skipped, no return values and no get speed command.")
    def test_setM0Speed(self):
        self._log.debug("Processing")

        for i in range(2):
            self._qik.setM0Speed(50)
            time.sleep(0.5)

    @unittest.skip("Skipped, no return values and no get speed command.")
    def test_setM1Speed(self):
        self._log.debug("Processing")

        for i in range(2):
            self._qik.setM1Speed(50)
            time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
