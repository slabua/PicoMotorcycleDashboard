# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard UTILS
"""

__author__ = "Salvatore La Bua"


# Utility functions
log_file = open("log.csv", "a")


def _log(data):
    log_file.write(str(data) + "\n")
    log_file.flush()


def ds_scan_roms(ds_sensor, resolution):
    roms = ds_sensor.scan()
    for rom in roms:
        if resolution == 9:
            config = b"\x00\x00\x1f"
        elif resolution == 10:
            config = b"\x00\x00\x3f"
        elif resolution == 11:
            config = b"\x00\x00\x5f"
        elif resolution == 12:
            config = b"\x00\x00\x7f"
        ds_sensor.write_scratch(rom, config)
    return roms


def map_range(value, in_range, out_range):
    (a, b), (c, d) = in_range, out_range
    return (value - a) / (b - a) * (d - c) + c


def moving_avg(value, array, n):
    if len(array) >= n:
        array.pop(0)
    array.append(value)

    return sum(array) / len(array)


def normalise_avg(avg, headings, neopixel_ring=None):
    # Check whether the array contains both positive and negative numbers
    has_positive = any(num > 270 for num in headings)
    has_negative = any(num < 90 for num in headings)

    if avg > 180:
        np_val = 360 - avg
    else:
        np_val = avg

    if has_positive and has_negative:
        if neopixel_ring is not None:
            neopixel_ring.set_np(0, (0, 0, 32))

        tmp_headings = []
        for h in headings:
            if h > 270:
                h = h - 360
            tmp_headings.append(h)
        avg = ((sum(tmp_headings) / len(tmp_headings)) + 360) % 360

        return avg

    if neopixel_ring is not None:
        neopixel_ring.set_np(0, (0, round(map_range(np_val, (180, 0), (0, 32))), 0))

    return avg


def read_adc(adc):
    return adc.read_u16()


def read_gps(gps):
    gps.update_gps(verbose=False)


def read_mpu(mpu):
    mpu.update_mpu()


def read_builtin_temp(adc):
    CONVERSION_FACTOR = 3.3 / 65535
    reading = read_adc(adc) * CONVERSION_FACTOR
    return 27 - (reading - 0.706) / 0.001721
