#
# central/rotaryencoder/rotary_encoder.py
#

"""
This is rotary encode code converted from the C code for the AVR series of
microcontrollers originally written by Peter Dannegger at:
http://www.mikrocontroller.net/articles/Drehgeber

by Carl J. Nobile
"""

from Adafruit_BBIO import GPIO


class RotaryEncoder(object):
    _DEFAULT_BOUNCE_TIME = 300

    def __init__(self, phaseA, phaseB):
        self._encDelta = 0
        self._last = 0
        self._phaseA = phaseA
        self._phaseB = phaseB
        self._bounceTime = self._DEFAULT_BOUNCE_TIME

    def setBounceTime(self, time):
        """
        Set the bounce time in ms.

        time - Time in milliseconds.
        """
        self._bounceTime = time

    def setPins(self):
        GPIO.setup(self._phaseA, GPIO.IN)
        GPIO.setup(self._phaseB, GPIO.IN)

    def initEncoder(self):
        new = 0

        if self._phaseA:
            new = 3

        if self._phaseB:
            new ^= 1

        self._last = new
        self._encDelta = 0;

    def enableInterrupts(self):
        """
        This sets the interrupt.
        """
        GPIO.add_event_detect(
            self._phaseA, GPIO.RISING, bouncetime=self._bounceTime,
            callback=self.__phaseAInterrupt)
        GPIO.add_event_detect(
            self._phaseB, GPIO.RISING, bouncetime=self._bounceTime,
            callback=self.__phaseBInterrupt)

    def disableInterrupts(self):
        """
        This clears the interrupt.
        """
        GPIO.remove_event_detect(self._phaseA)
        GPIO.remove_event_detect(self._phaseB)

    def __phaseAInterrupt(self):
        new = 0

        if self._phaseA:
            new = 3

        diff = self._last - new

        if diff & 1:
            self._last = new
            self._encDelta += (diff & 2) - 1

    def __phaseBInterrupt(self):
        new = 0

        if self._phaseB:
            new ^= 1

        diff = self._last - new

        if diff & 1:
            self._last = new
            self._encDelta += (diff & 2) - 1

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


if __name__ == '__main__':
    value = 0
    phaseA = 'p8_3'
    phaseB = 'p8_4'

    re = RotaryEncoder(phaseA, phaseB)
    re.setPins()
    re.initEncoder()
    re.enableInterrupts()

    while True:
        value = += re.encodeRead_1()
        # Set LEDs here. *** FIX ME ***
