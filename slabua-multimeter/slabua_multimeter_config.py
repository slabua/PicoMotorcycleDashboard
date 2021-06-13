# SLaBua Digital Multi Meter
# Config utility functions

import ujson


def initialise_config(CONFIG_FILE):
    LAYOUT_PEN_ID = 0
    RPM_LAYOUT_ID = 2
    SPLIT_BARS = True
    LARGE_BATTERY = True
    BATTERY_ICON_DISCRETE = False
    BV = 2

    config = {
        "LAYOUT_PEN_ID": LAYOUT_PEN_ID,
        "RPM_LAYOUT_ID": RPM_LAYOUT_ID,
        "SPLIT_BARS": SPLIT_BARS,
        "LARGE_BATTERY": LARGE_BATTERY,
        "BATTERY_ICON_DISCRETE": BATTERY_ICON_DISCRETE,
        "BV": BV
    }

    print("config initialised")
    with open(CONFIG_FILE, 'w') as config_file:
        ujson.dump(config, config_file)
    
    return [LAYOUT_PEN_ID, RPM_LAYOUT_ID, SPLIT_BARS, LARGE_BATTERY, BATTERY_ICON_DISCRETE, BV]
    
def read_config(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as config_file:
        config = ujson.load(config_file)
    
    LAYOUT_PEN_ID = config['LAYOUT_PEN_ID']
    RPM_LAYOUT_ID = config['RPM_LAYOUT_ID']
    SPLIT_BARS = config['SPLIT_BARS']
    LARGE_BATTERY = config['LARGE_BATTERY']
    BATTERY_ICON_DISCRETE = config['BATTERY_ICON_DISCRETE']
    BV = config['BV']

    return [LAYOUT_PEN_ID, RPM_LAYOUT_ID, SPLIT_BARS, LARGE_BATTERY, BATTERY_ICON_DISCRETE, BV]

def write_config(CONFIG_FILE, LAYOUT_PEN_ID, RPM_LAYOUT_ID, SPLIT_BARS, LARGE_BATTERY, BATTERY_ICON_DISCRETE, BV):
    config = {
        "LAYOUT_PEN_ID": LAYOUT_PEN_ID,
        "RPM_LAYOUT_ID": RPM_LAYOUT_ID,
        "SPLIT_BARS": SPLIT_BARS,
        "LARGE_BATTERY": LARGE_BATTERY,
        "BATTERY_ICON_DISCRETE": BATTERY_ICON_DISCRETE,
        "BV": BV
    }

    print("config updated")
    with open(CONFIG_FILE, 'w') as config_file:
        ujson.dump(config, config_file)
