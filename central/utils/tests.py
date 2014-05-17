#!/usr/bin/env python

"""
by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os, unittest
from unittest import skip

from central.utils.gpio import GPIO
from central.utils.exceptions import *


class TestGPIO(unittest.TestCase):

    def __init__(self, name):
        super(TestGPIO, self).__init__(name)
        self._isRoot = os.getuid() == 0

    def setUp(self):
        self.gpio = GPIO()

    def tearDown(self):
        self.gpio.cleanup()

    def test_isRootUser(self):
        self.assertTrue(self.gpio.isRootUser() == self._isRoot)

    def test__getGpioId(self):
        validPins = ('p8.7', 'p8_7', 'P8_7', 'gpio2_2', 'GPIO2.2', 'gpio_66',)
        validPin = 66
        msg = u"Invalid pin value found: {}, should have been: {}."

        for pin in validPins:
            gpioId = self.gpio._getGpioId(pin)
            self.assertTrue(gpioId == validPin, msg.format(gpioId, validPin))

        invalidPins = ('q8_7', 'gpio_125', '',)

        for pin in invalidPins:
            with self.assertRaises(InvalidPinNomenclatureException):
                gpioId = self.gpio._getGpioId(pin)
                print("Invalid result, should have failed, "
                      "gpioId: {}".format(gpioId))

    def test_setMode(self):
        # Test setMode with only first argument.
        pin = u'gpio_44'
        self.gpio.setMode(pin)
        result = self.getDirection(pin)
        self.assertTrue(result == 'out', msg=u"Invalid pin direction, found: "
                        u"'{}', should have been: 'out'".format(result))
        result = self.getEdge(pin)
        self.assertTrue(result == 'both', msg=u"Invalid pin edge, found: "
                        u"'{}', should have been: 'both'".format(result))
        result = self.getValue(pin)
        self.assertTrue(result == 0, msg=u"Invalid pin value, found: "
                        u"'{}', should have been: '0'".format(result))

        # Test setMode with all arguments.
        pin = u'gpio_67'
        directions = (GPIO.IN, GPIO.OUT,)
        edges = (GPIO.RISING, GPIO.FALLING, GPIO.BOTH,)

        for direction in directions:
            for edge in edges:
                kwargs = {u'direction': direction, u'edge': edge}
                self.gpio.setMode(pin, **kwargs)
                d = self.getDirection(pin)
                self.assertTrue(d == direction, msg=u"Invalid direction, "
                                u"found: {}, should have been: {}.".format(
                                    d, direction))
                e = self.getEdge(pin)
                self.assertTrue(e == edge, msg=u"Invalid edge, found: {}, "
                                u"should have been: {}.".format(e, edge)))
                self.cleanup(pin)

    def test_setDirection(self):
        pin = u'gpio_30'
        self.gpio.setMode(pin)
        self.gpio.setDirection(pin, GPIO.IN)
        d = self.getDirection(pin)
        self.assertTrue(d == GPIO.IN, msg=u"Invalid direction, found: {}, "
                        u"should have been: {}.".format(d, GPIO.IN))

    def test_setEdge(self):
        pin = u'gpio_30'
        self.gpio.setMode(pin)
        self.gpio.setEdge(pin, GPIO.FALLING)
        e = self.getEdge(pin)
        self.assertTrue(e == GPIO.FALLING, msg=u"Invalid edge, found: {}, "
                        u"should have been: {}.".format(e, GPIO.FALLING))

    def test_setValue(self):
        pin = u'gpio_30'
        self.gpio.setMode(pin)
        self.gpio.setValue(pin, 1)
        e = self.getValue(pin)
        self.assertTrue(e == GPIO.HIGH, msg=u"Invalid value, found: {}, "
                        u"should have been: {}.".format(e, GPIO.HIGH))


if __name__ == '__main__':
    unittest.main()
