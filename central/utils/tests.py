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

import logging
import os, select
import unittest
from unittest import skip

from central.utils.gpio import GPIO
from central.utils.events import Event
from central.utils.containers import Pin
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
        result = self.gpio.getDirection(pin)
        self.assertTrue(result == u'in', msg=u"Invalid pin direction, found: "
                        u"'{}', should have been: 'out'".format(result))
        result = self.gpio.getEdge(pin)
        self.assertTrue(result == u'none', msg=u"Invalid pin edge, found: "
                        u"'{}', should have been: 'both'".format(result))
        result = self.gpio.getValue(pin)
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
                d = self.gpio.getDirection(pin)
                self.assertTrue(d == direction, msg=u"Invalid direction, "
                                u"found: {}, should have been: {}.".format(
                                    d, direction))
                e = self.gpio.getEdge(pin)
                self.assertTrue(e == edge, msg=u"Invalid edge, found: {}, "
                                u"should have been: {}.".format(e, edge))
                self.gpio.cleanup(pin)

    def test_setDirection(self):
        pin = u'gpio_30'
        self.gpio.setMode(pin)
        self.gpio.setDirection(pin, GPIO.IN)
        d = self.gpio.getDirection(pin)
        self.assertTrue(d == GPIO.IN, msg=u"Invalid direction, found: {}, "
                        u"should have been: {}.".format(d, GPIO.IN))

    def test_setEdge(self):
        pin = u'gpio_30'
        self.gpio.setMode(pin)
        self.gpio.setEdge(pin, GPIO.FALLING)
        e = self.gpio.getEdge(pin)
        self.assertTrue(e == GPIO.FALLING, msg=u"Invalid edge, found: {}, "
                        u"should have been: {}.".format(e, GPIO.FALLING))

    def test_setValue(self):
        pin = u'gpio_30'
        self.gpio.setMode(pin, direction=GPIO.OUT)
        self.gpio.setValue(pin, GPIO.LOW)
        e = self.gpio.getValue(pin)
        self.assertTrue(e == GPIO.LOW, msg=u"Invalid value, found: {}, "
                        u"should have been: {}.".format(e, GPIO.LOW))


class TestPin(unittest.TestCase):

    def __init__(self, name):
        super(TestPin, self).__init__(name)

    def setUp(self):
        self.gpio = GPIO() #level=logging.DEBUG)

    def tearDown(self):
        self.gpio.cleanup()

    def test_isClosed(self):
        pin = u'gpio_3'
        self.gpio.setMode(pin)
        cont = Pin(pin) #, level=logging.DEBUG)
        result = cont.isClosed
        self.assertTrue(result == False, msg=u"Pin container property "
                        u"'isClosed' for pin '{}' should be 'False', found "
                        u"'{}'".format(pin, result))
        cont.close()
        result = cont.isClosed
        self.assertTrue(result == True, msg=u"Pin container property "
                        u"'isClosed' for pin '{}' should be 'True', found "
                        u"'{}'".format(pin, result))

    def test_direction(self):
        pin = u'gpio_4'
        directions = (GPIO.OUT, GPIO.IN,)
        self.gpio.setMode(pin)

        for d in directions:
            self.gpio.setDirection(pin, d)

            with Pin(pin) as cont:
                cd = cont.direction
                gd = self.gpio.getDirection(pin)
                self.assertTrue(cd == gd, msg=u"Pin container property "
                                u"'direction' is '{}', should be '{}'".format(
                                    cd, gd))

    def test_edge(self):
        pin = u'gpio_5'
        edges = (GPIO.RISING, GPIO.FALLING, GPIO.BOTH,)
        self.gpio.setMode(pin)

        for e in edges:
            self.gpio.setEdge(pin, e)

            with Pin(pin) as cont:
                ce = cont.edge
                ge = self.gpio.getEdge(pin)
                self.assertTrue(ce == ge, msg=u"Pin container property "
                                u"'edge' is '{}', should be '{}'".format(
                                    ce, ge))


class TestEvent(unittest.TestCase):

    def __init__(self, name):
        super(TestEvent, self).__init__(name)

    def setUp(self):
        self.gpio = GPIO()

    def tearDown(self):
        self.gpio.cleanup()

    def test_register(self):
        pin = u'gpio_44'
        self.gpio.setMode(pin, direction=GPIO.IN, edge=GPIO.RISING)

        with Pin(pin) as cont, Event() as event:
            event.register(cont)
            



            ## #while not event.hasInput(cont):

            ## try:
            ##     event.eventWait(timeout=0)
            ##     print "queue: {}\nevents: {},\ncontainers: {}".format(
            ##           event._queue, event._events, event._containers)

            ##     print "hasInput: {}".format(event.hasInput(cont))
            ##     print "hasOutput: {}".format(event.hasOutput(cont))
            ##     print "hasError: {}".format(event.hasError(cont))
            ##     print "hasHangup: {}".format(event.hasHangup(cont))
            ##     print "hasPriorityInput: {}".format(event.hasPriorityInput(cont))
            ## except select.error as e:
            ##     print e




if __name__ == '__main__':
    unittest.main()
