# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard
"""

__author__ = "Salvatore La Bua"
__copyright__ = "Copyright 2021, Salvatore La Bua"
__license__ = "GPL"
__version__ = "0.2.1"
__maintainer__ = "Salvatore La Bua"
__email__ = "slabua@gmail.com"
__status__ = "Development"

import gc
import math

import ds18x20
import machine
import onewire
import picomotodash_env as pmdenv
import qrcode
import utime
from picographics import (
    DISPLAY_PICO_DISPLAY,
    DISPLAY_PICO_DISPLAY_2,
    PEN_P4,
    PicoGraphics,
)
from pimoroni import RGBLED

gc.enable()
gc.threshold(100000)


# Timer
timer = machine.Timer()
start_time = utime.time()


# Parameters
STATE_FILE = "state.json"
CONFIG_FILE = "config.json"
USE_BG_IMAGE = False
BG_IMAGES = ["img0.jpg", "img1.jpg"]
LAYOUT_PEN_ID = 0
UPDATE_INTERVAL = 0.1
USE_TIMEOUT = 3
BUTTON_DEBOUNCE_TIME = 0.25
DS_RESOLUTION = 11
CLIP_MARGIN = 6
FUEL_RESERVE = 25
RPM_MAX = 12000
RPM_REDLINE = 10000
RPM_LAYOUT_ID = 2
SPLIT_BARS = True
LARGE_BATTERY = True
BATTERY_TH = [11, 12]
BATTERY_ICON_DISCRETE = False
TEMP_TH = [19, 24]
TEMP_X = 150
TEMP_X_OFFSET = 100
TEMP_X_SCROLL = -10
TEMP_BAR_OFFSET = 10
INFO_X = 250
INFO_X_MIN = -5000
INFO_X_SCROLL = -10
INFO_SCROLL_DELAY = 0.01
INFO_TEXT = "Salvatore La Bua - http://twitter.com/slabua"
QR_URL = "http://twitter.com/slabua"

BACKLIGHT_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
BV = 7

# TODO find a better order and make it dynamic (maybe as dictionary)
SCREENS = [
    "HOME",
    "BATTERY",
    "FUEL",
    "TEMPERATURE",
    "RPM",
    "STATS",
]


# Variables initialisation
[
    LAYOUT_PEN_ID,
    RPM_LAYOUT_ID,
    SPLIT_BARS,
    LARGE_BATTERY,
    BATTERY_ICON_DISCRETE,
    BV,
] = pmdenv.read_state(STATE_FILE)
[
    USE_BG_IMAGE,
    FUEL_RESERVE,
    RPM_MAX,
    RPM_REDLINE,
    BATTERY_TH,
    TEMP_TH,
    INFO_TEXT,
    QR_URL,
] = pmdenv.read_config(CONFIG_FILE)

temp_id = 0
onewire_sensors = 0

# TODO make this variable dynamic according to the number of sensors connected
temperature_matrix = [[], [], []]

in_use = False
temp_x_pos = TEMP_X
temp_x_shift = TEMP_X_SCROLL
info_x_pos = INFO_X

t = 0
current_screen = 0

last_press_time = 0


# Utility functions
def set_in_use(_):
    global in_use

    if in_use:
        in_use = not in_use
        timer.deinit()
        print("Timeout released.")


def in_use_led(in_use):
    if in_use:
        led.set_rgb(64, 0, 0)
    else:
        led.set_rgb(0, 0, 0)


def blink_led(duration, r, g, b):
    led.set_rgb(r, g, b)
    utime.sleep(duration)
    led.set_rgb(0, 0, 0)


def acq_adc(adc):
    return adc.read_u16()


def acq_temp(adc):
    CONVERSION_FACTOR = 3.3 / 65535
    reading = acq_adc(adc) * CONVERSION_FACTOR
    return 27 - (reading - 0.706) / 0.001721


def scale_value(value, min_value, max_value, max_range):
    return ((value - 0) / (max_range - 0)) * (max_value - min_value) + min_value


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


def set_temperature_pen(reading):
    if reading < TEMP_TH[0]:
        display.set_pen(bluePen)
    elif reading >= TEMP_TH[0] and reading < TEMP_TH[1]:
        display.set_pen(greenPen)
    else:
        display.set_pen(redPen)


def set_battery_pen(reading):
    if reading < BATTERY_TH[0]:
        display.set_pen(customPen255010010)
    elif reading >= BATTERY_TH[0] and reading < BATTERY_TH[1]:
        display.set_pen(customPen255128010)
    else:
        display.set_pen(customPen010255010)


def measure_qr_code(size, code):
    w, _ = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.set_pen(blackPen)
    display.rectangle(ox, oy, size, size)
    display.set_pen(whitePen)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(
                    ox + x * module_size, oy + y * module_size, module_size, module_size
                )


# GPIO
temp_builtin = machine.ADC(4)  # Built-in temperature sensor

ds_pin = machine.Pin(11)  # 1-Wire temperature sensors
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_scan_roms(ds_sensor, DS_RESOLUTION)

adc0 = machine.ADC(machine.Pin(26, machine.Pin.IN))  # Battery adc
adc1 = machine.ADC(machine.Pin(27, machine.Pin.IN))  # Fuel adc
adc2 = machine.ADC(machine.Pin(28, machine.Pin.IN))  # RPM adc


# Pico Display boilerplate
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, rotate=0, pen_type=PEN_P4)
width, height = display.get_bounds()
w_factor = width / 240
h_factor = height / 135
led = RGBLED(6, 7, 8)


# QR Code
code = qrcode.QRCode()
code.set_text(QR_URL)
max_size = min(width, height)

size, _ = measure_qr_code(max_size, code)
left = int((width // 2) - (size // 2))
top = int((height // 2) - (size // 2))


if USE_BG_IMAGE and width == 240:  # TODO check
    import jpegdec

    j = jpegdec.JPEG(display)
    j.open_file(BG_IMAGES[0])

    for y in range(height / 20):
        j.decode(0, height - (y * 20), jpegdec.JPEG_SCALE_FULL, dither=False)
        display.update()
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL, dither=False)

    display.update()
    utime.sleep(2)
    # TODO check
    # j.open_file(BG_IMAGES[1])

whitePen = display.create_pen(255, 255, 255)
redPen = display.create_pen(255, 0, 0)
greenPen = display.create_pen(0, 255, 0)
bluePen = display.create_pen(0, 0, 255)
cyanPen = display.create_pen(0, 255, 255)
magentaPen = display.create_pen(255, 0, 255)
yellowPen = display.create_pen(255, 255, 0)
blackPen = display.create_pen(0, 0, 0)
customPen255196000 = display.create_pen(255, 196, 0)
customPen255010010 = display.create_pen(255, 10, 10)
customPen255128010 = display.create_pen(255, 128, 10)
customPen010255010 = display.create_pen(10, 255, 10)

pens = [
    whitePen,
    redPen,
    greenPen,
    bluePen,
    cyanPen,
    magentaPen,
    yellowPen,
    blackPen,
]


def display_clear():
    display.set_pen(blackPen)
    display.clear()


def display_init(bv):
    display.set_backlight(bv)
    display_clear()

    display.update()


display_init(BACKLIGHT_VALUES[BV])

gc.collect()


# Buttons
button_a = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
button_b = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
button_x = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button_y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)


# def int_a(pin):
#     global in_use
#     global current_screen

#     button_a.irq(handler=None)
#     # state = machine.disable_irq()

#     print("Interrupted (A)")
#     if not in_use and current_screen != 0:
#         current_screen = 0
#     else:
#         current_screen = (current_screen + 1) % len(SCREENS)

#     in_use = True
#     timer.init(
#         freq=(1 / USE_TIMEOUT),
#         mode=machine.Timer.PERIODIC,
#         callback=set_in_use,
#     )

#     display.remove_clip()
#     display_clear()

#     utime.sleep(BUTTON_DEBOUNCE_TIME)
#     button_a.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_a)
#     # machine.enable_irq(state)

def int_a(pin):
    global in_use
    global current_screen
    global last_press_time

    # button_a.irq(handler=None)
    # state = machine.disable_irq()

    new_press_time = utime.ticks_ms()
    if (new_press_time - last_press_time) > (BUTTON_DEBOUNCE_TIME * 1000):

        print("Interrupted (A)")
        if not in_use and current_screen != 0:
            current_screen = 0
        else:
            current_screen = (current_screen + 1) % len(SCREENS)

        in_use = True
        timer.init(
            freq=(1 / USE_TIMEOUT),
            mode=machine.Timer.PERIODIC,
            callback=set_in_use,
        )

        display.remove_clip()
        display_clear()

        # utime.sleep(BUTTON_DEBOUNCE_TIME)
        # button_a.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_a)
        # machine.enable_irq(state)
        last_press_time = utime.ticks_ms()


def int_b(pin):
    global in_use
    global BV
    global SPLIT_BARS
    global info_x_pos
    global LAYOUT_PEN_ID
    global last_press_time

    # button_b.irq(handler=None)

    new_press_time = utime.ticks_ms()
    if (new_press_time - last_press_time) > (BUTTON_DEBOUNCE_TIME * 1000):

        print("Interrupted (B)")
        set_in_use(in_use)

        print("Used memory before cleanup: ", gc.mem_alloc())
        print("Available memory before cleanup: ", gc.mem_free())
        gc.collect()
        print("Used memory before cleanup: ", gc.mem_alloc())
        print("Available memory after cleanup: ", gc.mem_free())
        gc.collect()

        if not button_y.value():
            info_x_pos = INFO_X
            SPLIT_BARS = not SPLIT_BARS

            display.remove_clip()
            display_clear()

            while not button_y.value():
                if info_x_pos < INFO_X_MIN:
                    info_x_pos = INFO_X
                else:
                    info_x_pos += INFO_X_SCROLL

                display_clear()
                display.set_pen(greenPen)
                # display.text(INFO_TEXT, info_x_pos, 8, 10000, 16)

                draw_qr_code(left, top, max_size, code)

                display.update()

                utime.sleep(INFO_SCROLL_DELAY)

        if not button_x.value():
            if current_screen == 0:
                LAYOUT_PEN_ID = (LAYOUT_PEN_ID + 1) % len(pens)

            elif current_screen == 5:
                # TODO Debouncing might cause the config file overwriting
                # once again after initialisation
                [
                    LAYOUT_PEN_ID,
                    RPM_LAYOUT_ID,
                    SPLIT_BARS,
                    LARGE_BATTERY,
                    BATTERY_ICON_DISCRETE,
                    BV,
                ] = pmdenv.initialise_state(STATE_FILE)
                blink_led(0.2, 0, 255, 255)

        else:
            BV = (BV + 1) % len(BACKLIGHT_VALUES)
            display.set_backlight(BACKLIGHT_VALUES[BV])

        # utime.sleep(BUTTON_DEBOUNCE_TIME)
        # button_b.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_b)
        last_press_time = utime.ticks_ms()


def int_x(pin):
    global in_use
    global temp_id
    global temp_x_pos
    global temp_x_shift
    global BATTERY_ICON_DISCRETE
    global RPM_LAYOUT_ID
    global last_press_time

    # button_x.irq(handler=None)

    new_press_time = utime.ticks_ms()
    if (new_press_time - last_press_time) > (BUTTON_DEBOUNCE_TIME * 1000):

        print("Interrupted (X)")
        set_in_use(in_use)

        if current_screen == 0:
            if temp_x_shift == 0:
                temp_x_shift = TEMP_X_SCROLL
            else:
                temp_x_shift = 0
                temp_x_pos = TEMP_X

        elif current_screen == 1:
            BATTERY_ICON_DISCRETE = not BATTERY_ICON_DISCRETE

        elif current_screen == 3:
            temp_id = (temp_id + 1) % (1 + onewire_sensors)

        elif current_screen == 4:
            RPM_LAYOUT_ID = (RPM_LAYOUT_ID + 1) % 5

        elif current_screen == 5:
            pmdenv.write_state(
                STATE_FILE,
                LAYOUT_PEN_ID,
                RPM_LAYOUT_ID,
                SPLIT_BARS,
                LARGE_BATTERY,
                BATTERY_ICON_DISCRETE,
                BV,
            )
            blink_led(0.2, 0, 0, 255)

        # utime.sleep(BUTTON_DEBOUNCE_TIME)
        # button_x.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_x)
        last_press_time = utime.ticks_ms()


def int_y(pin):
    global in_use
    global temp_id
    global SPLIT_BARS
    global LARGE_BATTERY
    global start_time
    global temperature_matrix
    global last_press_time

    # button_y.irq(handler=None)

    new_press_time = utime.ticks_ms()
    if (new_press_time - last_press_time) > (BUTTON_DEBOUNCE_TIME * 1000):

        print("Interrupted (Y)")
        set_in_use(in_use)

        if current_screen in [0, 2, 4]:
            if onewire_sensors == 0 or temp_x_shift != 0:
                SPLIT_BARS = not SPLIT_BARS
            else:
                temp_id = (temp_id + 1) % (1 + onewire_sensors)

        elif current_screen == 1:
            LARGE_BATTERY = not LARGE_BATTERY

        elif current_screen == 3:
            temperature_matrix[temp_id] = []

        elif current_screen == 5:
            start_time = utime.time()

        # utime.sleep(BUTTON_DEBOUNCE_TIME)
        # button_y.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_y)
        last_press_time = utime.ticks_ms()


button_a.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_a)
button_b.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_b)
button_x.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_x)
button_y.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_y)


# Interface
def draw_home_layout(pen):
    display.set_pen(pen)
    display.rectangle(0, 0, width, 2)
    display.rectangle(0, 0, 2, height)
    display.rectangle(0, height - 2, width, 2)
    display.rectangle(width - 2, 0, 2, height)

    display.set_pen(blackPen)
    display.rectangle(0, 0, 2, 2)
    display.rectangle(width - 2, 0, 2, 2)
    display.rectangle(0, height - 2, 2, 2)
    display.rectangle(width - 2, height - 2, 2, 2)

    display.set_pen(pen)
    display.rectangle(1, 1, 2, 2)
    display.rectangle(width - 3, 1, 2, 2)
    display.rectangle(1, height - 3, 2, 2)
    display.rectangle(width - 3, height - 3, 2, 2)

    display.rectangle(0, round(height / 4), width, 2)
    display.rectangle(0, round(height / 2), width, 2)
    display.rectangle(0, round(height / 4 * 3), width, 2)


def draw_home_fuel():
    reading = scale_value(acq_adc(adc1), 0, 100, 65535)

    if reading < FUEL_RESERVE:
        display.set_pen(redPen)
    else:
        display.set_pen(customPen255196000)

    display.rectangle(
        100,
        round(h_factor * 5),
        round((width - 100 - CLIP_MARGIN) * reading / 100),
        round(h_factor * 25),
    )

    if SPLIT_BARS:
        display.set_pen(blackPen)
        for r in range(100, width - CLIP_MARGIN, 34):
            display.rectangle(r, round(h_factor * 5), 2, round(h_factor * 25))

    if reading < FUEL_RESERVE:
        display.set_pen(redPen)
        display.text("R", width - round(w_factor * 25), 8, width, round(h_factor * 3))


def draw_home_battery():
    reading = scale_value(acq_adc(adc0), 0, 16, 65535)

    set_battery_pen(reading)
    display.text(
        "{:.2f}".format(reading),
        round(w_factor * 150),
        8 + 1 * round(h_factor * 34),
        width,
        round(h_factor * 3),
    )


def draw_home_temperature():
    global temp_x_pos
    global temp_x_shift

    if not onewire_sensors:
        temp_x_shift = 0

    if temp_x_shift == 0:
        if temp_id == 0:
            temperature = acq_temp(temp_builtin)
        else:
            ds_sensor.convert_temp()
            temperature = ds_sensor.read_temp(roms[temp_id - 1])

        set_temperature_pen(temperature)
        display.text(
            "T" + str(temp_id) + ":",
            temp_x_pos - 50,
            8 + 2 * round(h_factor * 34),
            width,
            round(h_factor * 3),
        )
        display.text(
            "{:.2f}".format(temperature),
            round(w_factor * temp_x_pos) - round(w_factor * 3),
            8 + 2 * round(h_factor * 34),
            width,
            round(h_factor * 3),
        )

    else:
        temp_x_tn = TEMP_X_OFFSET
        temp_x_pos += temp_x_shift
        if temp_x_pos < -150:
            temp_x_pos = 250
        temperature = acq_temp(temp_builtin)

        set_temperature_pen(temperature)
        display.text(
            "{:.2f}".format(temperature),
            round(w_factor * temp_x_pos),
            8 + 2 * round(h_factor * 34),
            width,
            round(h_factor * 3),
        )

        try:
            ds_sensor.convert_temp()
        except onewire.OneWireError:
            pass

        for ows in range(onewire_sensors):
            temperature = ds_sensor.read_temp(roms[ows])

            set_temperature_pen(temperature)
            display.text(
                "{:.2f}".format(temperature),
                round(w_factor * temp_x_pos) + (temp_x_tn * (ows + 1)),
                8 + 2 * round(h_factor * 34),
                width,
                round(h_factor * 3),
            )


def draw_home_rpm():
    reading = scale_value(acq_adc(adc2), 0, RPM_MAX, 65535)

    at_redline_width = round((width - 100 - CLIP_MARGIN) * RPM_REDLINE / RPM_MAX)
    rpm_width = round((width - 100 - CLIP_MARGIN) * reading / RPM_MAX)
    redline_delta = rpm_width - at_redline_width

    display.set_pen(cyanPen)
    if reading > RPM_REDLINE:
        display.rectangle(
            100,
            round(h_factor * 5) + 3 * round(h_factor * 34),
            at_redline_width,
            round(h_factor * 24),
        )
        display.set_pen(redPen)
        display.rectangle(
            100 + at_redline_width,
            round(h_factor * 5) + 3 * round(h_factor * 34),
            redline_delta,
            round(h_factor * 24),
        )
    else:
        display.rectangle(
            100,
            round(h_factor * 5) + 3 * round(h_factor * 34),
            round((width - 100) * reading / RPM_MAX),
            round(h_factor * 24),
        )

    if SPLIT_BARS:
        display.set_pen(blackPen)
        for r in range(100, width - CLIP_MARGIN, 10):
            display.rectangle(
                r,
                round(h_factor * 5) + 3 * round(h_factor * 34),
                2,
                round(h_factor * 24),
            )


# Screens
def screen_home():
    display_clear()

    # Home
    draw_home_layout(pens[LAYOUT_PEN_ID])

    if LAYOUT_PEN_ID == 7:
        display.set_pen(whitePen)
    display.text("F  >", 10, 8, width, round(h_factor * 3))
    display.text("B  >", 10, 8 + 1 * round(h_factor * 34), width, round(h_factor * 3))
    display.text(
        "T  >",
        10,
        8 + 2 * round(h_factor * 34),
        width,
        round(h_factor * 3),
    )
    display.text("R  >", 10, 8 + 3 * round(h_factor * 34), width, round(h_factor * 3))

    display.set_clip(100, 0, width - 100 - CLIP_MARGIN, height)

    # Fuel
    draw_home_fuel()

    # Battery
    draw_home_battery()

    # Temperature
    draw_home_temperature()

    # RPM
    draw_home_rpm()

    display.remove_clip()
    display.update()


def screen_battery():
    display_clear()

    reading = scale_value(acq_adc(adc0), 0, 16, 65535)
    print("ADC0: " + str(reading))

    set_battery_pen(reading)
    display.rectangle(0, 0, width, round(135 / 3))

    display.set_pen(blackPen)
    display.text(SCREENS[current_screen], 8, 6, width, 5)

    if LARGE_BATTERY:
        batt_w_diff = 0
    else:
        batt_w_diff = 40

    set_battery_pen(reading)
    display.rectangle(12, 60, 16, 3)
    display.rectangle(19, 53, 3, 16)
    display.rectangle(10, 72, 20, 4)
    display.rectangle(0, 76, 80 - batt_w_diff, 49)
    if LARGE_BATTERY:
        display.rectangle(52 - batt_w_diff, 60, 16, 3)
        display.rectangle(50 - batt_w_diff, 72, 20, 4)

    display.set_pen(blackPen)
    display.rectangle(14, 75, 12, 3)
    display.rectangle(2, 78, 76 - batt_w_diff, 45)
    display.rectangle(0, 76, 3, 2)
    display.rectangle(77 - batt_w_diff, 76, 3, 2)
    display.rectangle(0, 123, 3, 2)
    display.rectangle(77 - batt_w_diff, 123, 3, 2)
    if LARGE_BATTERY:
        display.rectangle(54, 75, 12, 3)

    set_battery_pen(reading)
    if BATTERY_ICON_DISCRETE:
        if reading < 3:
            pass
        elif reading > 3 and reading < 5:
            display.rectangle(2, 116, 76 - batt_w_diff, 7)
        elif reading > 5 and reading < 8:
            display.rectangle(2, 103, 76 - batt_w_diff, 20)
        elif reading > 8 and reading < 11:
            display.rectangle(2, 90, 76 - batt_w_diff, 33)
        else:
            display.rectangle(2, 78, 76 - batt_w_diff, 45)
    else:
        if reading > 11:
            batt_level = 11
        else:
            batt_level = reading
        display.rectangle(
            2,
            78 + round(45 * (11 - batt_level) / 11),
            76 - batt_w_diff,
            45 - round(45 * (11 - batt_level) / 11),
        )

    display.rectangle(1, 77, 3, 2)
    display.rectangle(76 - batt_w_diff, 77, 3, 2)
    display.rectangle(1, 122, 3, 2)
    display.rectangle(76 - batt_w_diff, 122, 3, 2)

    if LARGE_BATTERY:
        display.text(
            "{:.1f}".format(reading) + "",
            round(w_factor * 90),
            round(h_factor * 71),
            width,
            9,
        )
    else:
        display.text(
            "{:.1f}".format(reading) + "",
            round(w_factor * 60),
            round(h_factor * 59),
            width,
            11,
        )

    display.set_pen(blackPen)
    display.rectangle(0, 87, 80 - batt_w_diff, 3)
    display.rectangle(0, 99, 80 - batt_w_diff, 3)
    display.rectangle(0, 111, 80 - batt_w_diff, 3)

    display.update()


def screen_fuel():
    display_clear()

    reading = scale_value(acq_adc(adc1), 0, 100, 65535)
    print("ADC1: " + str(reading))

    if reading < FUEL_RESERVE:
        display.set_pen(redPen)
    else:
        display.set_pen(customPen255196000)

    display.rectangle(
        0,
        round(height / 3 + 10),
        round(width * reading / 100),
        round(height / 3 * 2 - 10),
    )
    display.rectangle(0, 0, width, round(135 / 3))

    display.set_pen(blackPen)
    display.text(SCREENS[current_screen], 8, 6, width, 5)

    if SPLIT_BARS:
        for r in range(60, width, 60):
            display.rectangle(
                r,
                round(height / 3 + 10),
                3,
                round(height / 3 * 2 - 10),
            )

    if reading < FUEL_RESERVE:
        display.set_pen(redPen)
        display.text(
            "R",
            width - round(w_factor * 55),
            round(h_factor * 59),
            width,
            11,
        )

    display.update()


def screen_temperature():
    global temperature_matrix

    display_clear()

    temperatures = []
    if onewire_sensors:
        ds_sensor.convert_temp()
    utime.sleep_ms(round(750 / (2 ** (12 - DS_RESOLUTION))))
    temperatures.append(acq_temp(temp_builtin))
    for ows in range(onewire_sensors):
        temperatures.append(ds_sensor.read_temp(roms[ows]))

    for t in range(len(temperatures)):
        if len(temperature_matrix[t]) >= (width / TEMP_BAR_OFFSET):
            temperature_matrix[t].pop(0)
        temperature_matrix[t].append(temperatures[t])

    if isinstance(temperatures[temp_id], float):
        print("T" + str(temp_id) + ": " + str(temperatures[temp_id]))
    else:
        print("Temperature acquisition failed, retrying...")

    set_temperature_pen(temperatures[temp_id])
    display.rectangle(0, 0, width, round(135 / 3))

    curr_x = 0
    for t in temperature_matrix[temp_id]:
        set_temperature_pen(t)
        display.rectangle(
            curr_x,
            height - (round(t) * 2),
            TEMP_BAR_OFFSET - 2,
            round(t) * 2,
        )
        curr_x += TEMP_BAR_OFFSET

    display.set_pen(blackPen)
    display.text(
        "T" + str(temp_id) + ":  " + "{:.1f}".format(temperatures[temp_id]) + " c",
        8,
        6,
        width,
        5,
    )

    display.update()


def screen_rpm():
    display_clear()

    reading = scale_value(acq_adc(adc2), 0, RPM_MAX, 65535)
    print("ADC2: " + str(reading))

    at_redline_width = round(width * RPM_REDLINE / RPM_MAX)
    rpm_width = round(width * reading / RPM_MAX)
    redline_delta = rpm_width - at_redline_width

    display.set_pen(cyanPen)
    if reading > RPM_REDLINE:
        display.rectangle(
            0, round(height / 3 + 10), at_redline_width, round(height / 3 * 2 - 10)
        )
        display.set_pen(redPen)
        display.rectangle(
            at_redline_width,
            round(height / 3 + 10),
            redline_delta,
            round(height / 3 * 2 - 10),
        )
    else:
        display.rectangle(
            0,
            round(height / 3 + 10),
            round(width * reading / RPM_MAX),
            round(height / 3 * 2 - 10),
        )

    """
    if reading > RPM_REDLINE:
        display.set_pen(redPen)
    else:
        display.set_pen(cyanPen)
    display.rectangle(
        0,
        round(height / 3 + 10),
        round(width * reading / RPM_MAX),
        round(height / 3 * 2 - 10),
    )
    """

    if SPLIT_BARS:
        display.set_pen(blackPen)
        for r in range(20, width, 20):
            display.rectangle(
                r,
                round(height / 3 + 10),
                3,
                round(height / 3 * 2 - 10),
            )

    display.set_pen(blackPen)
    H = height / 3 * 2 - 10
    if RPM_LAYOUT_ID == 0:
        for x in range(0, width):
            display.rectangle(
                x,
                round(height / 3 + 10),
                1,
                round((height / 3 * 2 - 10) - ((height / 3 * 2 - 10) * (x / width))),
            )
    elif RPM_LAYOUT_ID == 1:
        for x in range(0, width):
            display.rectangle(
                x,
                round(height / 3 + 10),
                1,
                round(
                    (height / 3 * 2 - 10)
                    - ((height / 3 * 2 - 10) * (x / width))
                    + ((0.01 * x**2 - x) / 40)
                ),
            )
    elif RPM_LAYOUT_ID == 2:
        for x in range(0, width):
            display.rectangle(
                x,
                round(height / 3 + 10),
                1,
                round(
                    (height / 3 * 2 - 10)
                    - 0.8
                    * (
                        math.sqrt(
                            2
                            * H**2
                            * (
                                1
                                - (
                                    (x - (width - 0) * 2 - 0) ** 2
                                    / (width * 2 + 0) ** 2
                                )
                            )
                        )
                    )
                    + 0
                ),
            )
    elif RPM_LAYOUT_ID == 3:
        for x in range(0, width):
            display.rectangle(
                x,
                round(height / 3 + 10),
                1,
                round(
                    (height / 3 * 2 - 10)
                    - (
                        math.sqrt(
                            H**2 * (1 - ((x - width - 0) ** 2 / (width + 0) ** 2))
                        )
                    )
                    + 0
                ),
            )
    elif RPM_LAYOUT_ID == 4:
        for x in range(0, 80):
            display.rectangle(x, round(height / 3 + 10), 1, 20)

    display.set_pen(whitePen)
    display.text(SCREENS[current_screen], 8, 50, width, round(h_factor * 3))
    if reading >= RPM_REDLINE:
        display.set_pen(redPen)
    display.text("{:.0f}".format(reading), 8, 6, width, 6)

    display.update()


def screen_stats():
    display_clear()

    uptime = utime.time() - start_time
    print("Uptime: " + str(uptime))

    display.set_pen(whitePen)
    display.text(SCREENS[current_screen], 10, 8, width, round(h_factor * 3))

    display.set_pen(greenPen)
    display.text(str(uptime) + " s", 0, 70, width, round(h_factor * 6))

    display.update()


screen_functions = [
    screen_home,
    screen_battery,
    screen_fuel,
    screen_temperature,
    screen_rpm,
    screen_stats,
]

gc.collect()


# Main
spinner = "-\|/"


while True:
    utime.sleep(UPDATE_INTERVAL)

    in_use_led(in_use)

    roms = ds_scan_roms(ds_sensor, DS_RESOLUTION)
    if len(roms) != onewire_sensors:
        print("The number of connected 1-Wire devices has been updated.")
        onewire_sensors = len(roms)
        blink_led(0.2, 255, 255, 0)

    if current_screen not in [0, 1, 2, 3, 4, 5]:
        display_clear()
        display.set_pen(whitePen)
        display.text(SCREENS[current_screen], 10, 8, width, 3)

        display.update()
    else:
        print(spinner[t], end="\r")
        t = (t + 1) % len(spinner)

    screen_functions[current_screen]()

    utime.sleep(UPDATE_INTERVAL)
