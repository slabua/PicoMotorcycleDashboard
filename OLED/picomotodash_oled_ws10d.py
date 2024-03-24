# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard OLED
"""

__author__ = "Salvatore La Bua"
__copyright__ = "Copyright 2021, Salvatore La Bua"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Salvatore La Bua"
__email__ = "slabua@gmail.com"
__status__ = "Development"

import _thread
import framebuf
import gc
import math
import sh1107

from picomotodash_gps import GPS as pmdGPS
from picomotodash_mpu9250 import MPU as pmdMPU
from picomotodash_neopx import NEOPX as pdmNEOPX
from picomotodash_rpm import RPM as pmdRPM

from machine import Pin, PWM, SPI
from utime import sleep, sleep_us

gc.enable()
gc.threshold(100000)


# Display setup
key0 = Pin(15, Pin.IN, Pin.PULL_UP)
# key1 = Pin(17, Pin.IN, Pin.PULL_UP)
spi1 = SPI(1, baudrate=4_000_000, sck=Pin(10), mosi=Pin(11), miso=None)
display = sh1107.SH1107_SPI(128, 64, spi1, Pin(8), Pin(12), Pin(9), rotate=0)
display.contrast(0x80)
display.fill(0)
display.show()

# GPS setup
gps = pmdGPS(local_offset=9, location_formatting="dd")

# Magnetometer setup
mpu = pmdMPU()
# x_off = 28099.99
# y_off = 30178.57
# z_off = 43987.61
headings = []
HEADING = 0
labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]

# Neopixel setup
PIN_NUM = 3
NUM_LEDS = 37
neopixel_ring = pdmNEOPX(pin=PIN_NUM, n=NUM_LEDS)

# RPM setup
rpm_estimates = []
RPM_ESTIMATE = 0
PWM2RPM_FACTOR = 10


# Utility functions
log_file = open("log.csv", "a")


def _log(data):
    log_file.write(str(data) + "\n")
    log_file.flush()


def map_range(value, in_range, out_range):
    (a, b), (c, d) = in_range, out_range
    return (value - a) / (b - a) * (d - c) + c


def moving_avg(value, array, n):
    if len(array) >= n:
        array.pop(0)
    array.append(value)

    return sum(array) / len(array)


def normalise_avg(avg):
    # Check whether the array contains both positive and negative numbers
    has_positive = any(num > 270 for num in headings)
    has_negative = any(num < 90 for num in headings)

    if avg > 180:
        np_val = 360 - avg
    else:
        np_val = avg

    if has_positive and has_negative:
        neopixel_ring.set_np(0, (0, 0, 32))

        tmp_headings = []
        for h in headings:
            if h > 270:
                h = h - 360
            tmp_headings.append(h)
        avg = ((sum(tmp_headings) / len(tmp_headings)) + 360) % 360

        return avg

    neopixel_ring.set_np(0, (0, round(map_range(np_val, (180, 0), (0, 32))), 0))

    return avg


def moving_avg_backup(n):
    global headings

    if len(headings) >= n:
        headings.pop(0)

    headings.append(HEADING)

    # Check whether the array contains both positive and negative numbers
    has_positive = any(num > 270 for num in headings)
    has_negative = any(num < 90 for num in headings)

    avg = sum(headings) / len(headings)

    if avg > 180:
        np_val = 360 - avg
    else:
        np_val = avg

    if has_positive and has_negative:
        neopixel_ring.set_np(0, (0, 0, 32))

        tmp_headings = []
        for h in headings:
            if h > 270:
                h = h - 360
            tmp_headings.append(h)
        avg = ((sum(tmp_headings) / len(tmp_headings)) + 360) % 360

        return avg

    neopixel_ring.set_np(0, (0, round(map_range(np_val, (180, 0), (0, 32))), 0))

    return avg


def show_logo():
    with open("SLBLogo128x64_L.pbm", "rb") as f:
        f.readline()  # Magic number
        f.readline()  # Creator comment
        f.readline()  # Dimensions
        data = bytearray(f.read())
    fbuf_L = framebuf.FrameBuffer(data, 34, 64, framebuf.MONO_HLSB)

    with open("SLBLogo128x64_C.pbm", "rb") as f:
        f.readline()  # Magic number
        f.readline()  # Creator comment
        f.readline()  # Dimensions
        data = bytearray(f.read())
    fbuf_C = framebuf.FrameBuffer(data, 58, 64, framebuf.MONO_HLSB)

    with open("SLBLogo128x64_R.pbm", "rb") as f:
        f.readline()  # Magic number
        f.readline()  # Creator comment
        f.readline()  # Dimensions
        data = bytearray(f.read())
    fbuf_R = framebuf.FrameBuffer(data, 34, 64, framebuf.MONO_HLSB)

    display.contrast(255)
    # display.invert(1)
    # display.show()
    x_L = 32
    x_C = 35
    x_R = 62
    # display.blit(fbuf_C, x_C, 0)
    """
    display.blit(fbuf_L, x_L, 0)
    display.blit(fbuf_R, x_R, 0)
    display.fill_rect(62, 2, 2, 60, 1)

    display.show()
    utime.sleep(1)
    """

    for c in range(0, 128, 2):
        display.blit(fbuf_L, x_L, 0)
        display.blit(fbuf_R, x_R, 0)
        display.fill_rect(62, 2, 2, 60, 1)
        for r in range(0, 64, 2):
            display.line(c, r, 127, r, 0)
            display.line(0, r + 1, 127 - c, r + 1, 0)
        display.show()

    delay = 0.0000001
    for x in range(2, 33, 2):  # 34
        display.fill(0)
        delay = delay**0.88
        display.blit(fbuf_C, x_C, 0)
        display.blit(fbuf_L, round(x_L - x), 0)
        display.blit(fbuf_R, round(x_R + x), 0)
        # display.text("Loading...", 26, 30, 1)
        # display.text("Loading...", 25, 29, 0)
        display.show()
        sleep(delay)

    display.fill_rect(26, 30, 77, 8, 0)
    display.fill_rect(28, 30, 4, 8, 1)
    display.fill_rect(96, 30, 4, 8, 1)
    display.show()
    sleep(1)
    """
    display.blit(fbuf_L, 0, 0)
    display.blit(fbuf_C, x_C, 0)
    display.blit(fbuf_R, 94, 0)
    display.show()
    utime.sleep(10)
    """

    for c in range(0, 128, 2):
        display.blit(fbuf_L, 0, 0)
        display.blit(fbuf_C, x_C, 0)
        display.blit(fbuf_R, 94, 0)
        for r in range(0, 64, 2):
            display.line(0, r, c, r, 0)
            display.line(127 - c, r + 1, 127, r + 1, 0)
        display.show()

    display.fill(1)
    display.text("READY!", 41, 30, 1)
    display.text("READY!", 40, 29, 0)
    display.show()
    sleep(1)
    display.contrast(5)
    # display.invert(0)
    display.fill(0)
    display.show()


def read_gps():
    gps.update_gps(verbose=False)


def read_mpu():
    mpu.update_mpu()


def draw_compass():
    x_pos = round((360 - HEADING) / 360 * 240)

    for i in range(24):
        x_pos_off = (64 + (i * 10) + x_pos) % 240
        # display.line(x_post_off, 8, x_post_off, 28, 1)

        if x_pos_off >= 0 and x_pos_off <= 127:
            if x_pos_off < 64:
                x = x_pos_off / 64
                x = math.pow(abs(x), 2) * 64
            else:
                x = (128 - x_pos_off) / 64
                x = (64 - (math.pow(abs(x), 2) * 64)) + 64
            x = round(x)

            if i % 3 == 0:
                display.line(x, 3, x, 12, 1)
                label = labels[round(i / 3)]
                if len(label) == 1:
                    laboff = 4
                else:
                    laboff = 8

                display.text(label, x - laboff, 16, 1)
            else:
                display.line(x, 4, x, 8, 1)

            # display.text(str(round(x)), x, 36, 1)
            # display.show()

    display.line(0, 0, 127, 0, 1)
    display.fill_rect(62, 0, 5, 21, 0)

    display.triangle(56, 0, 72, 0, 64, 12, 0, True)
    display.triangle(60, 0, 68, 0, 64, 8, 1, True)
    display.pixel(59, 0, 1)
    # display.pixel(66, 5, 1)
    display.pixel(62, 5, 0)
    display.pixel(67, 3, 1)
    display.pixel(68, 1, 1)
    display.pixel(69, 0, 1)
    display.pixel(59, 1, 1)
    display.pixel(69, 1, 1)
    display.pixel(60, 2, 1)
    display.pixel(68, 2, 1)
    display.fill_rect(63, 0, 3, 20, 1)
    display.fill_rect(64, 6, 1, 13, 0)
    display.pixel(64, 20, 1)


def draw_icm():
    print(
        "Acceleration: X = %.3f,\tY = %.3f,\tZ = %.3f"
        % (mpu.imu[0], mpu.imu[1], mpu.imu[2])
    )
    print(
        "Gyroscope:    X = %.3f,\tY = %.3f,\tZ = %.3f"
        % (mpu.imu[3], mpu.imu[4], mpu.imu[5])
    )
    print(
        "Magnetic:     X = %.3f,\tY = %.3f,\tZ = %.3f"
        % (mpu.imu[6], mpu.imu[7], mpu.imu[8])
    )

    display.line(0, 26, 127, 26, 1)
    display.text("%.1f, %.1f, %.1f" % (mpu.imu[0], mpu.imu[1], mpu.imu[2]), 0, 30)
    display.text("%.1f, %.1f, %.1f" % (mpu.imu[3], mpu.imu[4], mpu.imu[5]), 0, 39)
    display.text("%.1f, %.1f, %.1f" % (mpu.imu[6], mpu.imu[7], mpu.imu[8]), 0, 48)


def draw_infobox():
    display.rect(0, 26, 128, 64 - 48, 1)
    # display.fill_rect(1, 29, 126, 64 - 50, 0)
    if len(str(round(HEADING))) == 1:
        laboff = 4
    elif len(str(round(HEADING))) == 2:
        laboff = 8
    else:
        laboff = 12
    # display.text(str(round(HEADING)), 66-laboff, 54, 1)
    # display.text(str(round(HEADING)), 65-laboff, 53, 0)
    display.text(str(round(HEADING)), 64 - 32 - laboff, 31, 1)

    if HEADING > 10 and HEADING < 180:
        display.triangle(4, 34, 8, 29, 8, 38, 1, True)
        display.text("N", 10, 31, 1)
    elif HEADING > 180 and HEADING < 350:
        display.triangle(64 - 3, 34, 64 - 8, 29, 64 - 8, 38, 1, True)
        display.pixel(64 - 3, 34, 0)
        display.text("N", 47, 31, 1)

    display.fill_rect(64, 28, 1, 12, 1)

    # display.text("R:" + f"{str(round(RPM_ESTIMATE)):>5}", 69, 31, 1)
    display.text("kph:" + f"{str(round(gps.speed)):>3}", 69, 31, 1)


def draw_gps():
    display.text(str(gps.longitude[1]), 0, 0, 1)
    display.text(str(gps.latitude[1]), 0, 9, 1)
    display.text(str(gps.longitude[0]), 20, 0, 1)
    display.text(str(gps.latitude[0]), 20, 9, 1)
    # display.text("Time:", 1, 40, 1)
    display.text(
        "GPS     %02d:%02d:%02d"
        % (gps.timestamp[0], gps.timestamp[1], gps.timestamp[2]),
        0,
        48,
        1,
    )
    display.text("Alt %d" % (gps.altitude), 0, 57, 1)


def draw_rpm():
    # print("RPM: %.3f" % RPM_ESTIMATE)

    display.rect(0, 45, 128, 64 - 45, 1)

    display.line(1, 45, 126, 45, 0)

    display.fill_rect(0, 47, int(12000 * 128 / 12000), 15, 1)

    x = int(RPM_ESTIMATE * 128 / 12000)
    display.triangle(x - 9, 47 + 15, x, 47 + 15, x, 47, 0, True)
    display.fill_rect(x, 47, 126 - x, 15, 0)
    display.line(0, 46, 0, 62, 1)
    display.line(127, 46, 127, 62, 1)

    for div in range(3, 28):
        display.line(div * 4 - 0, 46, div * 4 - 10, 62, 0)

    display.triangle(1, 46, 1, 58, 110 - 10, 46, 0, True)
    # display.line(104, 47, 104, 61, 1)

    for i in range(13):
        display.line(i * 11 - 1, 46, i * 11 - 1, 49, 0)
        display.pixel(i * 11 - 2, 49, 0)
        display.line(i * 11 - 2, 46, i * 11 - 2, 48, 1)
    display.line(1, 46, 1, 62, 0)
    display.line(126, 46, 126, 62, 0)

    """
    display.pixel(113, 51, (int(RPM_ESTIMATE) % 2))
    display.pixel(114, 51, (int(RPM_ESTIMATE) % 2))
    display.pixel(116, 51, (int(RPM_ESTIMATE) % 2))
    display.pixel(117, 51, (int(RPM_ESTIMATE) % 2))
    display.fill_rect(112, 52, 7, 2, (int(RPM_ESTIMATE) % 2))
    display.fill_rect(113, 54, 5, 1, (int(RPM_ESTIMATE) % 2))
    display.fill_rect(114, 55, 3, 1, (int(RPM_ESTIMATE) % 2))
    display.pixel(115, 56, (int(RPM_ESTIMATE) % 2))
    """

    display.text("R:" + f"{str(round(RPM_ESTIMATE)):>5}", 71, 54, 0)
    display.text("R:" + f"{str(round(RPM_ESTIMATE)):>5}", 69, 52, 1)

    neopixel_ring.set_np_rpm(RPM_ESTIMATE)


# GPIO setup
"""
pwm0 = PWM(Pin(0))
pwm0.freq(300)
pwm0.duty_u16(32768)
pwm1 = PWM(Pin(1))
pwm1.freq(600)
pwm1.duty_u16(32768)
"""
pwm2 = PWM(Pin(2))
pwm2.freq(800)
pwm2.duty_u16(32768)


def startup_rpm():
    global RPM_ESTIMATE
    global rpm_estimates

    rpm_estimates = []

    while RPM_ESTIMATE < 12000:
        sleep_us(50)
        RPM_ESTIMATE += 1
    while RPM_ESTIMATE > 1:
        sleep_us(50)
        RPM_ESTIMATE -= 1


def decrease_rpm():
    global RPM_ESTIMATE
    global rpm_estimates

    rpm_estimates = []

    while RPM_ESTIMATE > 1:
        sleep_us(200)
        RPM_ESTIMATE -= 1


def thread1(PWM2RPM_FACTOR):
    from utime import sleep

    global RPM_ESTIMATE
    global rpm_estimates

    sleep(0.5)

    rpm = pmdRPM(pin=22, factor=PWM2RPM_FACTOR)

    startup_rpm()

    while True:
        # read_gps()

        rpm.estimate_rpm()
        RPM_ESTIMATE = moving_avg(rpm.RPM_ESTIMATE, rpm_estimates, 10)

        if rpm.timeout:
            decrease_rpm()
            rpm.reset()


show_logo()

gc.collect()
# sleep(0.5)

_thread.start_new_thread(thread1, [PWM2RPM_FACTOR])

PAGE_ID = 0
PAGES = 4

# Main loop
try:
    while True:
        # print(gc.mem_alloc())

        if key0.value() == 1:
            # sleep(0.1)
            read_gps()

            read_mpu()
            HEADING = mpu.heading
            HEADING = moving_avg(HEADING, headings, 5)  # 9
            HEADING = normalise_avg(HEADING)

            # neopixel_ring.update(RPM_ESTIMATE, HEADING)

            # print(key0.value(), key1.value())

            display.fill(0)

            if PAGE_ID == 0:
                draw_compass()
                draw_infobox()
                draw_rpm()
                pass
            elif PAGE_ID == 1:
                draw_compass()
                draw_icm()
                # draw_infobox()
                # draw_rpm()
            elif PAGE_ID == 2:
                # draw_compass()
                draw_gps()
                draw_infobox()
                # draw_rpm()
            elif PAGE_ID == 3:
                # draw_compass()
                # draw_infobox()
                draw_rpm()

            display.show()
        else:
            sleep(0.2)
            PAGE_ID = (PAGE_ID + 1) % PAGES

except KeyboardInterrupt:
    exit()
