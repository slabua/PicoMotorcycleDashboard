# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard DS18x20
"""

__author__ = "Salvatore La Bua"

from ds18x20 import DS18X20 as DS
from machine import Pin
from onewire import OneWire, OneWireError
from utime import sleep_ms


ds_pin = Pin(1)  # 1-Wire temperature sensors
DS_RESOLUTION = 11


class DS18X20:

    def __init__(self, pin=ds_pin, resolution=DS_RESOLUTION):

        self.pin = pin
        self.resolution = resolution

        self.ds_sensor = DS(OneWire(self.pin))
        self.roms = self.ds_scan_roms(self.ds_sensor, self.resolution)

        self.temperatures = []

    def ds_scan_roms(self, ds_sensor, resolution):
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

    def update_roms(self):
        self.roms = self.ds_scan_roms(self.ds_sensor, self.resolution)

    def update_temps(self):

        if len(self.roms) > 0:
            try:
                self.ds_sensor.convert_temp()
            except OneWireError:
                print("Cannot access the sensor.")
            else:
                sleep_ms(round(750 / (2 ** (12 - DS_RESOLUTION))))

                self.temperatures = []
                for r in range(len(self.roms)):
                    self.temperatures.append(self.ds_sensor.read_temp(self.roms[r]))

        return self.temperatures

    def read_nth(self, nth):
        self.update()

        return self.ds_sensor.read_temp(self.roms[nth])
