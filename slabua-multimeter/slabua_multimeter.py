# SLaBua Digital Multi Meter

import machine
import utime
import onewire, ds18x20


timer = machine.Timer()


# GPIO
sensor_temp = machine.ADC(4)
CONVERSION_FACTOR = 3.3 / (65535)
temp_id = 0

ds_pin = machine.Pin(11)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
onewire_sensors = 0

adc0 = machine.ADC(machine.Pin(26))
adc1 = machine.ADC(machine.Pin(27))
adc2 = machine.ADC(machine.Pin(28))


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

display_init(0.75)


# Buttons
BUTTON_DEBOUNCE_TIME = 0.2

button_a = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
button_b = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
button_x = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button_y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

def int_a(pin):
    """Screen selection"""
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
    
    display_clear()
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_a.irq(handler=int_a)
    #machine.enable_irq(state)

def int_b(pin):
    """TODO currently ALL SCREENS Brightness selection, later perhaps Palette selection"""
    global in_use
    global bv
    
    button_b.irq(handler=None)
    
    print("Interrupted (B)")
    set_in_use(in_use)
    
    bv = (bv + 1) % len(BACKLIGHT_VALUES)
    display.set_backlight(BACKLIGHT_VALUES[bv])
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_b.irq(handler=int_b)

def int_x(pin):
    """SCREEN 3 Temperature source selection"""
    global in_use
    global temp_id
    global current_x
    
    button_x.irq(handler=None)
    
    print("Interrupted (X)")
    set_in_use(in_use)
    
    if current_screen == 3:
        display_clear()
        current_x = 0
        temp_id = (temp_id + 1) % (1 + onewire_sensors)
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_x.irq(handler=int_x)

def int_y(pin):
    """TODO SCREEN 3 Clear view"""
    global in_use
    global current_x
    
    button_y.irq(handler=None)
    
    print("Interrupted (Y)")
    set_in_use(in_use)
    
    if current_screen == 3:
        display_clear()
        current_x = 0
    
    utime.sleep(BUTTON_DEBOUNCE_TIME)
    button_y.irq(handler=int_y)

button_a.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_a)
button_b.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_b)
button_x.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_x)
button_y.irq(trigger=machine.Pin.IRQ_FALLING, handler=int_y)


# Interface
USE_TIMEOUT = 3

in_use = False
current_x = 0

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

BACKLIGHT_VALUES = [0.25, 0.5, 0.75, 1.0]
bv = 2

SCREENS = ["HOME", "BATTERY", "FUEL", "TEMPERATURE", "RPM", "STATS"]  # TODO find a better order and make it dynamic (maybe as dictionary)
current_screen = 0


# Screens
temp_x = 150
def screen_home():
    global temp_x
    
    #print(current_screen)
    
    display_clear()
    
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
    
    display.rectangle(0, int(height / 4), width, 2)
    display.rectangle(0, int(height / 2), width, 2)
    display.rectangle(0, int(height / 4 * 3), width, 2)
    #display.text(SCREENS[current_screen], 10, 8, width, 3)
    
    display.text("Fuel", 10, 8, width, 3)
    display.text("Batt", 10, 41, width, 3)
    display.text("Temp", 10, 75, width, 3)
    display.text("RPM", 10, 108, width, 3)
    
    display.set_clip(100, 0, 240-100-10, height)
    
    # Battery
    reading = scale_value(acq_adc(adc0), 0, 15)
    
    if reading < 11:  # TODO move to a function with interval and colours, same for other if-else switches
        display.set_pen(255, 10, 10)
    elif reading >= 11 and reading < 12:
        display.set_pen(255, 128, 10)
    else:
        display.set_pen(10, 255, 10)
    
    display.text("{:.2f}".format(reading), 150, 41, width, 3)
    display.set_pen(whitePen)
    
    # Temperature
    temp_x_offset = 100
    temp_x -= 10
    if temp_x < -150:
        temp_x = 250
    #reading = sensor_temp.read_u16() * CONVERSION_FACTOR
    #temperature = 27 - (reading - 0.706) / 0.001721
    temperature = acq_temp(sensor_temp)
    
    display.set_pen(greenPen)
    
    if temperature > 24:  # TODO move to a function with interval and colours, same for other if-else switches
        display.set_pen(redPen)
    if temperature < 19:
        display.set_pen(bluePen)
    
    display.text("{:.2f}".format(temperature), temp_x, 75, width, 3)
    display.set_pen(whitePen)
    
    ds_sensor.convert_temp()
    #utime.sleep_ms(250)
    for ows in range(onewire_sensors):
        temperature = ds_sensor.read_temp(roms[ows])
        display.set_pen(greenPen)
        if temperature > 24:  # TODO move to a function with interval and colours, same for other if-else switches
            display.set_pen(redPen)
        if temperature < 19:
            display.set_pen(bluePen)
        display.text("{:.2f}".format(temperature), temp_x + (temp_x_offset * (ows + 1)), 75, width, 3)
    
    display.remove_clip()
    
    display.update()
    #utime.sleep(0.25)

def screen_battery():
    reading = scale_value(acq_adc(adc0), 0, 15)
    print("ADC0: " + str(reading))
    
    display_clear()
    
    display.set_pen(whitePen)
    display.text(SCREENS[current_screen], 10, 8, width, 3)
    
    if reading < 11:  # TODO move to a function with interval and colours, same for other if-else switches
        display.set_pen(255, 10, 10)
    elif reading >= 11 and reading < 12:
        display.set_pen(255, 128, 10)
    else:
        display.set_pen(10, 255, 10)
    
    display.rectangle(12, 55, 16, 3)
    display.rectangle(19, 48, 3, 16)
    display.rectangle(52, 55, 16, 3)
    display.rectangle(10, 67, 20, 4)
    display.rectangle(50, 67, 20, 4)
    display.rectangle(0, 71, 80, 49)
    
    display.set_pen(blackPen)
    display.rectangle(2, 73, 76, 45)
    display.rectangle(0, 71, 3, 2)
    display.rectangle(77, 71, 3, 2)
    display.rectangle(0, 118, 3, 2)
    display.rectangle(77, 118, 3, 2)
    
    if reading < 11:  # TODO move to a function with interval and colours, same for other if-else switches
        display.set_pen(255, 10, 10)
    elif reading >= 11 and reading < 12:
        display.set_pen(255, 128, 10)
    else:
        display.set_pen(10, 255, 10)
    
    if reading < 3:
        pass
    elif reading > 3 and reading < 5:
        display.rectangle(2, 111, 76, 7)
    elif reading > 5 and reading < 8:
        display.rectangle(2, 98, 76, 20)
    elif reading > 8 and reading < 11:
        display.rectangle(2, 85, 76, 33)
    else:
        display.rectangle(2, 73, 76, 45)
    
    display.rectangle(1, 72, 3, 2)
    display.rectangle(76, 72, 3, 2)
    display.rectangle(1, 117, 3, 2)
    display.rectangle(76, 117, 3, 2)
    
    display.text("{:.1f}".format(reading) + "", 90, 65, width, 9)
    
    display.set_pen(blackPen)
    display.rectangle(0, 82, 80, 3)
    display.rectangle(0, 94, 80, 3)
    display.rectangle(0, 106, 80, 3)
    
    display.update()
    utime.sleep(0.5)

def screen_fuel():
    print(current_screen)

def screen_temperature():
    global current_x
    
    #print(current_screen)
    
    if temp_id == 0:
        # the following two lines do some maths to convert the number from the temp sensor into celsius
        utime.sleep(0.75)
        temperature = acq_temp(sensor_temp)
    else:
        ds_sensor.convert_temp()
        utime.sleep_ms(750)
        #utime.sleep(1)
        temperature = ds_sensor.read_temp(roms[temp_id - 1])
        #for rom in roms:
        #    print(ds_sensor.read_temp(rom))
        #time.sleep(0.5)
        ##if isinstance(temp, float):
        ##    temp = temp * (9/5) + 32.0
        ##    print(temp, end=' ')
        ##    print('Valid temperature')
    
    if isinstance(temperature, float):
        print("T" + str(temp_id) + ": " + str(temperature))
    else:
        print("Temperature acquisition failed, retrying...")
    
    # this if statement clears the display once the graph reaches the right hand side of the display
    if current_x >= (width):
        display_clear()
        current_x = 0
    #if display.is_pressed(display.BUTTON_Y):
    #    print("Pressed (y)")
    #    current_x = 0
    #    display_clear()
    
    # chooses a pen colour based on the temperature
    display.set_pen(greenPen)
    
    if temperature > 24:  # TODO move to a function with interval and colours, same for other if-else switches
        display.set_pen(redPen)
    if temperature < 19:
        display.set_pen(bluePen)
        
    # heck lets also set the LED to match
    #display.set_led(0, 64, 0)
    #if temperature > 24:
    #    display.set_led(64, 0, 0)
    #if temperature < 21:
    #    display.set_led(0, 0, 64)
    
    # draws the reading as a tall, thin rectangle
    display.rectangle(current_x, height - (int(temperature) * 2), 8, height)
    
    # draws a white background for the text
    #display.set_pen(255, 255, 255)
    display.rectangle(1, 1, width, int(height / 3))
    
    # writes the reading as text in the white rectangle
    display.set_pen(blackPen)
    display.text("T" + str(temp_id) + ":  " + "{:.1f}".format(temperature) + " c", 8, 6, width, 5)
    
    # time to update the display
    display.update()
    
    # waits for 5 seconds
    #utime.sleep(0.5) 
    
    # the next tall thin rectangle needs to be drawn 5 pixels to the right of the last one
    current_x += 10

def screen_rpm():
    print(current_screen)

def screen_stats():
    print(current_screen)

screen_functions = [screen_home, screen_battery, screen_fuel, screen_temperature, screen_rpm, screen_stats]


# Utility functions
def acq_adc(adc):
    return adc.read_u16()
    #reading = reading / 65535 * 15

def scale_value(value, min_value, max_value):
    return ((value - 0) / (65535 - 0)) * (max_value - min_value) + min_value

def acq_temp(adc):
    reading = acq_adc(adc) * CONVERSION_FACTOR
    return 27 - (reading - 0.706) / 0.001721

def blink_led(duration, r, g, b):
    display.set_led(r, g, b)
    utime.sleep(duration)
    display.set_led(0, 0, 0)


# Main
loading = ['-', '\\', '|', '/']
t = 0

while True:
    utime.sleep(0.5)
    
    in_use_led(in_use)
    
    #print(SCREENS[current_screen])
    
    roms = ds_sensor.scan()
    if len(roms) != onewire_sensors:
        print("The number of connected 1-Wire devices has been updated.")
        onewire_sensors = len(roms)
        blink_led(0.2, 255, 255, 0)
    
    if current_screen != 0 and current_screen != 1 and current_screen != 3:
        display_clear()
        display.set_pen(whitePen)
        display.text(SCREENS[current_screen], 10, 8, width, 3)
        
        display.update()
    else:
        print(loading[t])
        t = (t + 1) % len(loading)
    
    screen_functions[current_screen]()
