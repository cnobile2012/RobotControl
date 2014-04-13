#
# central/rotaryencoder/rotary_encoder.py
#

"""
This is rotary encoder code converted from the C code for the AVR series of
microcontrollers originally written by Peter Dannegger at:
http://www.mikrocontroller.net/articles/Drehgeber

by Carl J. Nobile

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import thread

from Adafruit_BBIO import GPIO

_lock = thread.allocate_lock()


class RotaryEncoder(object):
    _DEFAULT_BOUNCE_TIME = 300

    def __init__(self, phaseA, phaseB):
        self._encDelta = 0
        self._last = 0
        self._phaseA = phaseA
        self._phaseB = phaseB
        self._setPins()
        self._bounceTime = self._DEFAULT_BOUNCE_TIME

    def _setPins(self):
        GPIO.setup(self._phaseA, GPIO.IN)
        GPIO.setup(self._phaseB, GPIO.IN)

    def resetPins(self):
        pass

    def setBounceTime(self, time):
        """
        Set the bounce time in ms.

        time - Time in milliseconds.
        """
        self._bounceTime = time

    def initEncoder(self):
        new = 0

        if GPIO.input(self._phaseA):
            new = 3

        if GPIO.input(self._phaseB):
            new ^= 1

        self._last = new
        self._encDelta = 0;

    def _phaseAInterrupt(self, channel):
        if not _lock.acquire(0): return

        try:
            new = 0

            if GPIO.input(channel):
                new = 3

            diff = self._last - new

            if diff & 1:
                self._last = new
                self._encDelta += (diff & 2) - 1
        except Exception, e:
            print e

        _lock.release()

    def _phaseBInterrupt(self, channel):
        if not _lock.acquire(0): return

        try:
            new = 0

            if GPIO.input(channel):
                new ^= 1

            diff = self._last - new

            if diff & 1:
                self._last = new
                self._encDelta += (diff & 2) - 1

        except Exception, e:
            print e

        _lock.release()

    def enableInterrupts(self):
        """
        This sets the interrupt.
        """
        GPIO.add_event_detect(
            self._phaseA, GPIO.RISING, bouncetime=self._bounceTime,
            callback=self._phaseAInterrupt)
        GPIO.add_event_detect(
            self._phaseB, GPIO.RISING, bouncetime=self._bounceTime,
            callback=self._phaseBInterrupt)

    def disableInterrupts(self):
        """
        This clears the interrupt.
        """
        GPIO.remove_event_detect(self._phaseA)
        GPIO.remove_event_detect(self._phaseB)

    def encodeRead_1(self):
        self.disableInterrupts()
        value = self._encDelta
        self._encDelta = 0;
        self.enableInterrupts()
        return value

    def encodeRead_2(self):
        self.disableInterrupts()
        value = self._encDelta
        self._encDelta &= 1;
        self.enableInterrupts()
        return value >> 1

    def encodeRead_4(self):
        self.disableInterrupts()
        value = self._encDelta
        self._encDelta &= 3;
        self.enableInterrupts()
        return value >> 2


def test(phaseA, phaseB, header, startPin):
    from central.utils import setupPins

    value = 0
    re = RotaryEncoder(phaseA, phaseB)
    re.initEncoder()
    re.enableInterrupts()
    #setupPins(header, startPin)

    while True:
        value += re.encodeRead_2()
        print value
        # Set LEDs here. *** FIX ME ***


if __name__ == '__main__':
    phaseA = 'P8_7'
    phaseB = 'P8_8'
    header = 8
    startPin = 9
    test(phaseA, phaseB, header, startPin)
