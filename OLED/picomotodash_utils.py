# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard UTILS
"""

__author__ = "Salvatore La Bua"


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


# def moving_avg_backup(n):
#     global headings

#     if len(headings) >= n:
#         headings.pop(0)

#     headings.append(HEADING)

#     # Check whether the array contains both positive and negative numbers
#     has_positive = any(num > 270 for num in headings)
#     has_negative = any(num < 90 for num in headings)

#     avg = sum(headings) / len(headings)

#     if avg > 180:
#         np_val = 360 - avg
#     else:
#         np_val = avg

#     if has_positive and has_negative:
#         neopixel_ring.set_np(0, (0, 0, 32))

#         tmp_headings = []
#         for h in headings:
#             if h > 270:
#                 h = h - 360
#             tmp_headings.append(h)
#         avg = ((sum(tmp_headings) / len(tmp_headings)) + 360) % 360

#         return avg

#     neopixel_ring.set_np(0, (0, round(map_range(np_val, (180, 0), (0, 32))), 0))

#     return avg
