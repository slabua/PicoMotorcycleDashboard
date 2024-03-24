# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard NEOPX
"""

__author__ = "Salvatore La Bua"


from machine import Pin
import neopixel

PIN_NUM = 3
NUM_LEDS = 37
RGBW = False

MODE_RPM = 0
MODE_COMPASS = 1
MODE_BLEND = 2


class NEOPX:

    def __init__(self, pin=PIN_NUM, n=NUM_LEDS, rgbw=RGBW):

        self.n = n
        self.np = neopixel.NeoPixel(Pin(pin), n, bpp=4 if rgbw else 3, timing=1)

        self.mode = MODE_COMPASS

    def map_range(self, value, in_range, out_range):
        (a, b), (c, d) = in_range, out_range
        return (value - a) / (b - a) * (d - c) + c

    def off(self):
        for i in range(self.n):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def set_np(self, i, rgb_tuple):
        self.np[i] = rgb_tuple
        self.np.write()

    def set_np_rpm(self, rpm):
        self.off()

        upto = rpm // 1000
        for i in range(24, upto + 24):
            self.np[i] = (2, 2, 0)

        self.np.write()

    def set_np_compass(self, heading):
        # TODO Update logic

        self.off()

        i = int(self.map_range(heading, (0, 360), (34, 24)))
        self.np[i] = (0, 0, 5)

        self.np.write()

    def set_np_blend(self, rpm, heading):
        # TODO Update logic

        self.off()

        upto = rpm // 1000
        for i in range(24, upto + 24):
            self.np[i] = (2, 2, 0)

        i = int(self.map_range(heading, (0, 360), (34, 24)))
        self.np[i] = (0, 0, 5)

        self.np.write()

    def update(self, rpm, heading):
        # TODO Update logic

        if self.mode == MODE_RPM:
            self.set_np_rpm(rpm)
        elif self.mode == MODE_COMPASS:
            self.set_np_compass(heading)
        elif self.mode == MODE_BLEND:
            self.set_np_blend(rpm, heading)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass


if __name__ == "__main__":
    off = (0, 0, 0)
    red = (10, 0, 0)
    green = (0, 10, 0)
    blue = (0, 0, 10)
    cyan = (0, 10, 10)
    yellow = (10, 10, 0)
    orange = (10, 2, 0)

    ring = NEOPX(3, 38)

    ring.np[0 + 21] = green
    ring.np[1 + 21] = blue
    ring.np[2 + 21] = yellow
    for i in range(3, 11):
        ring.np[i + 21] = cyan
    for i in range(11, 14):
        ring.np[i + 21] = orange
    ring.np[14 + 21] = yellow
    ring.np[15 + 21] = red

    ring.np.write()
