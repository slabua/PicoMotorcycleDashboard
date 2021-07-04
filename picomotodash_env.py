# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard
"""

# Config utility functions

import ujson

__author__ = "Salvatore La Bua"


def initialise_state(STATE_FILE):
    LAYOUT_PEN_ID = 0
    RPM_LAYOUT_ID = 2
    SPLIT_BARS = True
    LARGE_BATTERY = True
    BATTERY_ICON_DISCRETE = False
    BV = 2

    state = {
        "LAYOUT_PEN_ID": LAYOUT_PEN_ID,
        "RPM_LAYOUT_ID": RPM_LAYOUT_ID,
        "SPLIT_BARS": SPLIT_BARS,
        "LARGE_BATTERY": LARGE_BATTERY,
        "BATTERY_ICON_DISCRETE": BATTERY_ICON_DISCRETE,
        "BV": BV
    }

    print("state initialised")
    with open(STATE_FILE, 'w') as state_file:
        ujson.dump(state, state_file)
    
    return [LAYOUT_PEN_ID, RPM_LAYOUT_ID, SPLIT_BARS, LARGE_BATTERY, BATTERY_ICON_DISCRETE, BV]
    
def read_state(STATE_FILE):
    with open(STATE_FILE, 'r') as state_file:
        state = ujson.load(state_file)
    
    LAYOUT_PEN_ID = state['LAYOUT_PEN_ID']
    RPM_LAYOUT_ID = state['RPM_LAYOUT_ID']
    SPLIT_BARS = state['SPLIT_BARS']
    LARGE_BATTERY = state['LARGE_BATTERY']
    BATTERY_ICON_DISCRETE = state['BATTERY_ICON_DISCRETE']
    BV = state['BV']

    return [LAYOUT_PEN_ID, RPM_LAYOUT_ID, SPLIT_BARS, LARGE_BATTERY, BATTERY_ICON_DISCRETE, BV]

def write_state(STATE_FILE, LAYOUT_PEN_ID, RPM_LAYOUT_ID, SPLIT_BARS, LARGE_BATTERY, BATTERY_ICON_DISCRETE, BV):
    state = {
        "LAYOUT_PEN_ID": LAYOUT_PEN_ID,
        "RPM_LAYOUT_ID": RPM_LAYOUT_ID,
        "SPLIT_BARS": SPLIT_BARS,
        "LARGE_BATTERY": LARGE_BATTERY,
        "BATTERY_ICON_DISCRETE": BATTERY_ICON_DISCRETE,
        "BV": BV
    }

    print("state updated")
    with open(STATE_FILE, 'w') as state_file:
        ujson.dump(state, state_file)

def read_config(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as config_file:
        config = ujson.load(config_file)
    
    USE_BG_IMAGE = config['USE_BG_IMAGE']
    BG_IMAGE_SLOW_LOADING = config['BG_IMAGE_SLOW_LOADING']
    FUEL_RESERVE = config['FUEL_RESERVE']
    RPM_MAX = config['RPM_MAX']
    RPM_REDLINE = config['RPM_REDLINE']
    BATTERY_TH = config['BATTERY_TH']
    TEMP_TH = config['TEMP_TH']
    INFO_TEXT = config['INFO_TEXT']

    return [USE_BG_IMAGE, BG_IMAGE_SLOW_LOADING, FUEL_RESERVE, RPM_MAX, RPM_REDLINE, BATTERY_TH, TEMP_TH, INFO_TEXT]
