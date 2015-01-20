#!/usr/bin/env python
#
# motors/pololu/tests.py
#

import unittest
import time

from motors.pololu import Qik2s9v1


class TestQik2s9v1(unittest.TestCase):
    """
    Unit tests for the Qik 2s9v1 motor controller.
    """
    _DEFAULT_TTY = '/dev/ttyUSB0'
    _PORTOCOL_MAP = {0: "Pololu Protocol", 1: "Compact Protocol"}

    def __init__(self, name):
        super(TestQik2s9v1, self).__init__(name)

    def setUp(self):
        self._qik = Qik2s9v1(self._DEFAULT_TTY, readTimeout=5)

    def tearDown(self):
        if self._qik.isOpen():
            self._qik.setDeviceID(self._qik.DEFAULT_DEVICE_ID)
            self._qik.getError()
            self._qik.setPWMFrequency(31500)
            self._qik.setMotorShutdown(True)
            self._qik.setSerialTimeout(0.0)
            self._qik.setM0Speed(0)
            self._qik.setM0Coast()
            self._qik.setM1Speed(0)
            self._qik.setM1Coast()
            self._qik.close()

    def test_close(self):
        self.assertTrue(self._qik.isOpen() == True)
        self._qik.close()
        self.assertTrue(self._qik.isOpen() == False)

    def test_setCompactProtocol(self):
        """
        The compact protocol is not the default.
        """
        self.assertTrue(self._qik.isCompactProtocol() == False)
        self._qik.setCompactProtocol()
        self.assertTrue(self._qik.isCompactProtocol() == True)

    def test_setPololuProtocol(self):
        """
        The pololu portocol is the default.
        """
        self.assertTrue(self._qik.isPololuProtocol() == True)
        self._qik.setCompactProtocol()
        self.assertTrue(self._qik.isPololuProtocol() == False)

    def test_getFirmwareVersion(self):
        self.assertTrue(self._qik.getFirmwareVersion() in (1, 2))
        self._qik.setCompactProtocol()
        self.assertTrue(self._qik.getFirmwareVersion() in (1, 2))

    # Test for Data Overrun Error

    # Test for Frame Error

    # Test for CRC Error

    def test_getError_FormatError(self):
        command = 0x70 # Works in both protocols
        error = 64

        for i in range(2):
            self._qik._writeData(command, self._qik.DEFAULT_DEVICE_ID)
            result = self._qik.getError(message=False)
            msg = "{}: Invalid result '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, error)
            self.assertTrue(result == error, msg=msg)
            self._qik._writeData(command, self._qik.DEFAULT_DEVICE_ID)
            result = self._qik.getError()
            msg = "{}: Invalid result '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, self._qik._ERRORS.get(error))
            self.assertTrue(result == self._qik._ERRORS.get(error), msg=msg)
            self._qik.setCompactProtocol()

    def test_getError_TimeoutError(self):
        timeout = 0.262
        error = 128

        for i in range(2):
            self._qik.setSerialTimeout(timeout)
            time.sleep(0.263)
            result = self._qik.getError(message=False)
            msg = "{}: Invalid result '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, error)
            self.assertTrue(result == error, msg=msg)
            time.sleep(0.263)
            result = self._qik.getError()
            msg = "{}: Invalid result '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, self._qik._ERRORS.get(error))
            self.assertTrue(result == self._qik._ERRORS.get(error), msg=msg)
            self._qik.setCompactProtocol()

    @unittest.skip("Temporary skipped")
    def test_getDeviceID(self):
        devices = (self._qik.DEFAULT_DEVICE_ID, 127)

        for i in range(2):
            result = self._qik.getDeviceID()
            msg = "{}: Invalid device '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, devices[0])
            self.assertTrue(result == devices[0], msg=msg)
            self._qik.setDeviceID(devices[1])
            result = self._qik.getDeviceID()
            msg = "{}: Invalid device '{}' should be '{}'.".format(
                self._PORTOCOL_MAP.get(i), result, devices[1])
            self.assertTrue(result == devices[1], msg=msg)









if __name__ == '__main__':
    unittest.main()
