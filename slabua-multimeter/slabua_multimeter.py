# SLaBua Digital Multi Meter

import machine
import utime
import onewire, ds18x20


timer = machine.Timer()
start_time = utime.time()


# Parameters
UPDATE_INTERVAL = 0.1
USE_TIMEOUT = 3
BUTTON_DEBOUNCE_TIME = 0.2
DS_RESOLUTION = 11
CLIP_MARGIN = 6
FUEL_RESERVE = 25
RPM_MAX = 12000
RPM_REDLINE = 10000
SPLIT_BARS = True
LARGE_BATTERY = True
BATTERY_TH = [11, 12]
BATTERY_ICON_DISCRETE = False
TEMP_TH = [19, 24]
TEMP_X = 150
TEMP_X_OFFSET = 100
TEMP_X_SCROLL = -10
INFO_X = 250
INFO_X_MIN = -5000
INFO_X_SCROLL = -10
INFO_TEXT = "Salvatore La Bua - http://twitter.com/slabua"

BACKLIGHT_VALUES = [0.25, 0.5, 0.75, 1.0]
BV = 2

SCREENS = ["HOME", "BATTERY", "FUEL", "TEMPERATURE", "RPM", "STATS"]  # TODO find a better order and make it dynamic (maybe as dictionary)


# Variables initialisation
temp_id = 0
onewire_sensors = 0

in_use = False
current_x = 0
temp_x_pos = TEMP_X
temp_x_shift = TEMP_X_SCROLL
info_x_pos = INFO_X

t = 0
current_screen = 0


# Utility functions
def set_in_use(_):
    global in_use
    
    if in_use:
        in_use = not in_use
        timer.deinit()
        print("timeout")

def in_use_led(in_use):
    if in_use:
        display.set_led(64, 0, 0)
    else:
        display.set_led(0, 0, 0)

def blink_led(duration, r, g, b):
    display.set_led(r, g, b)
    utime.sleep(duration)
    display.set_led(0, 0, 0)

def acq_adc(adc):
    return adc.read_u16()

def acq_temp(adc):
    CONVERSION_FACTOR = 3.3 / (65535)
    reading = acq_adc(adc) * CONVERSION_FACTOR
    return 27 - (reading - 0.706) / 0.001721

def scale_value(value, min_value, max_value):
    return ((value - 0) / (65535 - 0)) * (max_value - min_value) + min_value

def ds_scan_roms(ds_sensor, resolution):
    roms = ds_sensor.scan()
    for rom in roms:
        if resolution == 9:
            config = b'\x00\x00\x1f'
        elif resolution == 10:
            config = b'\x00\x00\x3f'
        elif resolution == 11:
            config = b'\x00\x00\x5f'
        elif resolution == 12:
            config = b'\x00\x00\x7f'
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
        display.set_pen(255, 10, 10)
    elif reading >= BATTERY_TH[0] and reading < BATTERY_TH[1]:
        display.set_pen(255, 128, 10)
    else:
        display.set_pen(10, 255, 10)


# GPIO
temp_builtin = machine.ADC(4)

ds_pin = machine.Pin(11)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_scan_roms(ds_sensor, DS_RESOLUTION)

adc0 = machine.ADC(machine.Pin(26))  # Battery
adc1 = machine.ADC(machine.Pin(27))  # Fuel
adc2 = machine.ADC(machine.Pin(28))  # RPM


# Pico Display boilerplate
import picodisplay as display
width = display.get_width()
height = display.get_height()
display_buffer = bytearray(width * height * 2)
display.init(display_buffer)

whitePen = display.create_pen(255, 255, 255)
redPen = display.create_pen(255, 0, 0)
greenPen = display.create_pen(0, 255, 0)
bluePen = display.create_pen(0, 0, 255)
cyanPen = display.create_pen(0, 255, 255)
magentaPen = display.create_pen(255, 0, 255)
yellowPen = display.create_pen(255, 255, 0)
blackPen = display.create_pen(0, 0, 0)

pens = [whitePen, redPen, greenPen, bluePen, cyanPen, magentaPen, yellowPen, blackPen]  # TODO check

def display_clear():
    display.set_pen(blackPen)
    display.clear()

def display_init(bv):
    display.set_backlight(bv)
    display_clear()
    display.update()

display_init(BACKLIGHT_VALUES[BV])


# Buttons
button_a = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
button_b = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
button_x = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button_y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

def int_a(pin):
    global in_use
    global current_screen
    global current_x
    
    button_a.irq(handler=None)
    #state = machine.disable_irq()
    
    print("Interrupted (A)")
    if not in_use and current_screen != 0:
        current_screen = 0
    else:
        current_screen = (current_screen + 1) % len(SCREENS)
    
    current_x = 0
    
    in_use = True
    timer.init(freq=(1 / USE_TIMEOUT), mode=machine.Timer.PERIODIC, callback=set_in_use)
    
    display.remove_clip()
    display_clear()
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_a.irq(handler=int_a)
    #machine.enable_irq(state)

def int_b(pin):
    global in_use
    global BV
    global SPLIT_BARS
    global info_x_pos
    
    button_b.irq(handler=None)
    
    print("Interrupted (B)")
    set_in_use(in_use)
    
    if display.is_pressed(display.BUTTON_Y):
        info_x_pos = INFO_X
        SPLIT_BARS = not SPLIT_BARS
        
        display.remove_clip()
        display_clear()
        
        while display.is_pressed(display.BUTTON_Y):
            if info_x_pos < INFO_X_MIN:
                info_x_pos = INFO_X
            else:
                info_x_pos += INFO_X_SCROLL
            
            display_clear()
            display.set_pen(greenPen)
            display.text(INFO_TEXT, info_x_pos, 8, 10000, 16)
            
            display.update()
            
            utime.sleep(0.01)
    
    BV = (BV + 1) % len(BACKLIGHT_VALUES)
    display.set_backlight(BACKLIGHT_VALUES[BV])
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_b.irq(handler=int_b)

def int_x(pin):
    global in_use
    global temp_id
    global current_x
    global temp_x_pos
    global temp_x_shift
    global BATTERY_ICON_DISCRETE
    
    button_x.irq(handler=None)
    
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
        display_clear()
        current_x = 0
        temp_id = (temp_id + 1) % (1 + onewire_sensors)
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_x.irq(handler=int_x)

def int_y(pin):
    global in_use
    global current_x
    global temp_id
    global SPLIT_BARS
    global LARGE_BATTERY
    
    button_y.irq(handler=None)
    
    print("Interrupted (Y)")
    set_in_use(in_use)
    
    if current_screen == 0:
        if onewire_sensors == 0 or temp_x_shift != 0:
            SPLIT_BARS = not SPLIT_BARS
        else:
            temp_id = (temp_id + 1) % (1 + onewire_sensors)
    
    elif current_screen == 1:
        LARGE_BATTERY = not LARGE_BATTERY
    
    elif current_screen == 3:
        display_clear()
        current_x = 0
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_y.irq(handler=int_y)

button_a.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_a)
button_b.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_b)
button_x.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_x)
button_y.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_y)


# Interface
def draw_home_layout():
    display.set_pen(whitePen)
    display.rectangle(0, 0, width, height)
    
    display.set_pen(blackPen)
    display.rectangle(2, 2, width - 4, height - 4)
    display.rectangle(0, 0, 2, 2)
    display.rectangle(width - 2, 0, 2, 2)
    display.rectangle(0, height - 2, 2, 2)
    display.rectangle(width - 2, height - 2, 2, 2)
    
    display.set_pen(whitePen)
    display.rectangle(1, 1, 2, 2)
    display.rectangle(width - 3, 1, 2, 2)
    display.rectangle(1, height - 3, 2, 2)
    display.rectangle(width - 3, height - 3, 2, 2)
    
    display.rectangle(0, round(height / 4), width, 2)
    display.rectangle(0, round(height / 2), width, 2)
    display.rectangle(0, round(height / 4 * 3), width, 2)

def draw_home_fuel():
    reading = scale_value(acq_adc(adc1), 0, 100)
    
    display.set_pen(255, 196, 0)
    if reading < FUEL_RESERVE:
        display.set_pen(redPen)
        display.text("R", width - 25, 8, width, 3)
    display.rectangle(100, 5, round((width - 100 - CLIP_MARGIN) * reading / 100), 25)
    
    if SPLIT_BARS:
        display.set_pen(blackPen)
        for r in range(100, width - CLIP_MARGIN, 34):
            display.rectangle(r, 5, 2, 25)
    
    display.set_pen(whitePen)

def draw_home_battery():
    reading = scale_value(acq_adc(adc0), 0, 15)
    
    set_battery_pen(reading)
    
    display.text("{:.2f}".format(reading), 150, 41, width, 3)
    display.set_pen(whitePen)

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
        
        display.text("T" + str(temp_id) + ":", temp_x_pos - 50, 75, width, 3)
        display.text("{:.2f}".format(temperature), temp_x_pos, 75, width, 3)
        display.set_pen(whitePen)
        
    else:
        temp_x_tn = TEMP_X_OFFSET
        temp_x_pos += temp_x_shift
        # TODO Refactor these values
        if temp_x_pos < -150:
            temp_x_pos = 250
        temperature = acq_temp(temp_builtin)
        
        set_temperature_pen(temperature)
        
        display.text("{:.2f}".format(temperature), temp_x_pos, 75, width, 3)
        display.set_pen(whitePen)
        
        try:
            ds_sensor.convert_temp()
        except onewire.OneWireError:
            pass
        
        for ows in range(onewire_sensors):
            temperature = ds_sensor.read_temp(roms[ows])
            
            set_temperature_pen(temperature)
            
            display.text("{:.2f}".format(temperature), temp_x_pos + (temp_x_tn * (ows + 1)), 75, width, 3)

def draw_home_rpm():
    reading = scale_value(acq_adc(adc2), 0, RPM_MAX)
    
    at_redline_width = round((width - 100 - CLIP_MARGIN) * RPM_REDLINE / RPM_MAX)
    rpm_width = round((width - 100 - CLIP_MARGIN) * reading / RPM_MAX)
    redline_delta = rpm_width - at_redline_width
    
    display.set_pen(cyanPen)
    if reading > RPM_REDLINE:
        display.rectangle(100, 106, at_redline_width, 24)
        display.set_pen(redPen)
        display.rectangle(100 + at_redline_width, 106, redline_delta, 24)
    else:
        display.rectangle(100, 106, round((width - 100) * reading / RPM_MAX), 24)
    
    if SPLIT_BARS:
        display.set_pen(blackPen)
        for r in range(100, width - CLIP_MARGIN, 10):
            display.rectangle(r, 106, 2, 24)

# Screens
def screen_home():
    display_clear()
    
    # Home
    draw_home_layout()
    
    display.text("Fuel", 10, 8, width, 3)
    display.text("Batt", 10, 41, width, 3)
    display.text("Temp", 10, 75, width, 3)
    display.text("RPM", 10, 108, width, 3)
    
    display.set_clip(100, 0, 240 - 100 - CLIP_MARGIN, height)
    
    # Fuel
    draw_home_fuel()
    
    # Battery
    draw_home_battery()
    
    # Temperature
    draw_home_temperature()

    # RPM
    draw_home_rpm()

    display.set_pen(whitePen)
    
    display.remove_clip()
    
    display.update()

def screen_battery():
    reading = scale_value(acq_adc(adc0), 0, 15)
    print("ADC0: " + str(reading))
    
    display_clear()
    
    display.set_pen(whitePen)
    display.text(SCREENS[current_screen], 10, 8, width, 3)
    
    set_battery_pen(reading)
    
    if LARGE_BATTERY:
        batt_w_diff = 0
    else:
        batt_w_diff = 40
        
    display.rectangle(12, 55, 16, 3)
    display.rectangle(19, 48, 3, 16)
    display.rectangle(10, 67, 20, 4)
    display.rectangle(0, 71, 80 - batt_w_diff, 49)
    if LARGE_BATTERY:
        display.rectangle(52 - batt_w_diff, 55, 16, 3)
        display.rectangle(50 - batt_w_diff, 67, 20, 4)
    
    display.set_pen(blackPen)
    display.rectangle(14, 70, 12, 3)
    display.rectangle(2, 73, 76 - batt_w_diff, 45)
    display.rectangle(0, 71, 3, 2)
    display.rectangle(77 - batt_w_diff, 71, 3, 2)
    display.rectangle(0, 118, 3, 2)
    display.rectangle(77 - batt_w_diff, 118, 3, 2)
    if LARGE_BATTERY:
        display.rectangle(54, 70, 12, 3)
    
    set_battery_pen(reading)
    
    if BATTERY_ICON_DISCRETE:
        if reading < 3:
            pass
        elif reading > 3 and reading < 5:
            display.rectangle(2, 111, 76 - batt_w_diff, 7)
        elif reading > 5 and reading < 8:
            display.rectangle(2, 98, 76 - batt_w_diff, 20)
        elif reading > 8 and reading < 11:
            display.rectangle(2, 85, 76 - batt_w_diff, 33)
        else:
            display.rectangle(2, 73, 76 - batt_w_diff, 45)
    else:
        if reading > 11:
            batt_level = 11
        else:
            batt_level = reading
        display.rectangle(2, 73 + round(45 * (11 - batt_level) / 11), 76 - batt_w_diff, 45 - round(45 * (11 - batt_level) / 11))
    
    display.rectangle(1, 72, 3, 2)
    display.rectangle(76 - batt_w_diff, 72, 3, 2)
    display.rectangle(1, 117, 3, 2)
    display.rectangle(76 - batt_w_diff, 117, 3, 2)
    
    if LARGE_BATTERY:
        display.text("{:.1f}".format(reading) + "", 90, 66, width, 9)
    else:
        display.text("{:.1f}".format(reading) + "", 60, 54, width, 11)
    
    display.set_pen(blackPen)
    display.rectangle(0, 82, 80 - batt_w_diff, 3)
    display.rectangle(0, 94, 80 - batt_w_diff, 3)
    display.rectangle(0, 106, 80 - batt_w_diff, 3)
    
    display.update()
    utime.sleep(UPDATE_INTERVAL)

def screen_fuel():
    print(current_screen)
    
    reading = acq_adc(adc1)
    print(reading)

def screen_temperature():
    global current_x
    
    if temp_id == 0:
        utime.sleep_ms(round(750 / (2** (12 - DS_RESOLUTION))))
        temperature = acq_temp(temp_builtin)
    else:
        ds_sensor.convert_temp()
        utime.sleep_ms(round(750 / (2** (12 - DS_RESOLUTION))))
        temperature = ds_sensor.read_temp(roms[temp_id - 1])
        
    if isinstance(temperature, float):
        print("T" + str(temp_id) + ": " + str(temperature))
    else:
        print("Temperature acquisition failed, retrying...")
    
    if current_x >= (width):
        display_clear()
        current_x = 0
    
    set_temperature_pen(temperature)
        
    display.rectangle(current_x, height - (int(temperature) * 2), 8, height)
    display.rectangle(1, 1, width, int(height / 3))
    
    display.set_pen(blackPen)
    display.text("T" + str(temp_id) + ":  " + "{:.1f}".format(temperature) + " c", 8, 6, width, 5)
    
    display.update()
    
    current_x += 10

def screen_rpm():
    print(current_screen)

def screen_stats():
    uptime = utime.time() - start_time
    print("Uptime: " + str(uptime))
    
    display_clear()
    
    display.set_pen(whitePen)
    display.text(SCREENS[current_screen], 10, 8, width, 3)
    
    display.set_pen(greenPen)
    display.text(str(utime.time() - start_time) + " s", 0, 66, width, 9)
    
    display.update()

screen_functions = [screen_home, screen_battery, screen_fuel, screen_temperature, screen_rpm, screen_stats]


# Main
loading = ['-', '\\', '|', '/']

while True:
    utime.sleep(UPDATE_INTERVAL)
    
    in_use_led(in_use)
    
    roms = ds_scan_roms(ds_sensor, DS_RESOLUTION)
    if len(roms) != onewire_sensors:
        print("The number of connected 1-Wire devices has been updated.")
        onewire_sensors = len(roms)
        blink_led(0.2, 255, 255, 0)
    
    if current_screen not in [0, 1, 3, 5]:
        display_clear()
        display.set_pen(whitePen)
        display.text(SCREENS[current_screen], 10, 8, width, 3)
        
        display.update()
    else:
        print(loading[t])
        t = (t + 1) % len(loading)
    
    screen_functions[current_screen]()
