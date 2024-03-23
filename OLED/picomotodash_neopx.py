# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard NEOPX
"""

__author__ = "Salvatore La Bua"


from machine import Pin
import neopixel

PIN_NUM = 3
NUM_LEDS = 37
RGBW = False


class NEOPX:

    def __init__(self, pin=PIN_NUM, n=NUM_LEDS, rgbw=RGBW):

        self.n = n
        self.np = neopixel.NeoPixel(Pin(pin), n, bpp=4 if rgbw else 3, timing=1)

    def map_range(self, value, in_range, out_range):
        (a, b), (c, d) = in_range, out_range
        return (value - a) / (b - a) * (d - c) + c

    def set_np(self, i, rgb_tuple):
        self.np[i] = rgb_tuple
        self.np.write()

    def set_np_rpm(self, value):
        upto = value // 1000
        for i in range(24, self.n):
            if i < upto + 24:
                self.np[i] = (2, 2, 0)
            else:
                self.np[i] = (0, 0, 0)

        self.np.write()

    def reset(self):
        for i in range(self.n):
            self.np[i] = (0, 0, 0)
        self.np.write()

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
