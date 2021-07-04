# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard
"""

# Background utility functions

__author__ = "Salvatore La Bua"


def load_bg_image(display, height, width, display_buffer, is_slow, src_img):
    dst_img = src_img[0:-4] + ".img"

    if is_slow:
        create_bg_image(display, height, width, display_buffer, is_slow, src_img)
    else:
        try:
            restore = open(dst_img, 'rb')
            restore.readinto(display_buffer)
            restore.close()
        except OSError:
            create_bg_image(display, height, width, display_buffer, is_slow, src_img)

def create_bg_image(display, height, width, display_buffer, is_slow, src_img):
    dst_img = src_img[0:-4] + ".img"
    try:
        image_file = open(src_img, 'rb')
        image_file.seek(48)
        
        for y in range(height):
            for x in range(width):
                b = int.from_bytes(image_file.read(1), 'big')
                g = int.from_bytes(image_file.read(1), 'big')
                r = int.from_bytes(image_file.read(1), 'big')
                display.set_pen(r, g, b)
                display.pixel(x, height - y)
            display.update()
        image_file.close()
        saveFile = open(dst_img, 'wb')
        saveFile.write(display_buffer)
        saveFile.close()
    except OSError:
        print("Background image not found, skipping.")
