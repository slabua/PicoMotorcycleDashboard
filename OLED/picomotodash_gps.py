# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard GPS
"""

__author__ = "Salvatore La Bua"


from L76 import l76x
from L76.micropyGPS.micropyGPS import MicropyGPS
from utime import sleep

UARTx = 0
BAUDRATE = 9600


class GPS:

    def __init__(
        self, uartx=UARTx, _baudrate=BAUDRATE, local_offset=9, location_formatting="dd"
    ):

        self.gnss_l76b = l76x.L76X(uartx=uartx, _baudrate=_baudrate)
        self.gnss_l76b.l76x_exit_backup_mode()
        self.gnss_l76b.l76x_send_command(self.gnss_l76b.SET_SYNC_PPS_NMEA_ON)
        self.parser = MicropyGPS(
            local_offset=local_offset, location_formatting=location_formatting
        )
        # self.parser.start_logging("log.txt")
        # self.sentence = ""

        self.altitude = 0
        self.geoid_height = 0
        self.hdop = 0
        self.latitude = [0, 0]
        self.longitude = [0, 0]
        self.satellites_in_use = 0
        self.speed = -1
        self.timestamp = [0, 0, 0]

    def reset(self):
        self.RPM_ESTIMATE = 0
        self.duty = 50
        self.n_repeats = 1
        self.timeout = False

    def update_gps(self, verbose="v"):
        # parser.update(chr(gnss_l76b.uart_receive_byte()[0]))
        # my_sentence = "$GPRMC,081836,A,3751.65,S,14507.36,E,000.0,360.0,130998,011.3,E*62"
        # for x in my_sentence:
        #     parser.update(x)
        #     print(x)

        # sleep(0.1)

        if self.gnss_l76b.uart_any():
            sentence = self.parser.update(chr(self.gnss_l76b.uart_receive_byte()[0]))

            if sentence:

                self.altitude = self.parser.altitude
                self.geoid_height = self.parser.geoid_height
                self.hdop = self.parser.hdop
                self.latitude = self.parser.latitude
                self.longitude = self.parser.longitude
                self.satellites_in_use = self.parser.satellites_in_use
                self.speed = self.parser.speed[2]
                self.timestamp = self.parser.timestamp

                if verbose == "v":
                    self.print_gps_data()

            if verbose == "vv":
                self.print_gps_data()

        if verbose == "vvv":
            self.print_gps_data()

    def print_gps_data(self):
        print(
            "WGS84 Coordinate: Latitude(%c), Longitude(%c) %.9f,%.9f"
            % (
                self.latitude[1],
                self.longitude[1],
                self.latitude[0],
                self.longitude[0],
            )
        )
        print(
            "Timestamp: %d:%d:%d"
            % (
                self.timestamp[0],
                self.timestamp[1],
                self.timestamp[2],
            )
        )
        print("Fix Status:", self.parser.fix_stat)

        print("Altitude:%d m" % (self.altitude))
        print("Height Above Geoid:", self.geoid_height)
        print("Horizontal Dilution of Precision:", self.hdop)
        print("Satellites in Use by Receiver:", self.satellites_in_use)
        print("Speed:", self.speed)
        print("")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass


if __name__ == "__main__":
    gps = GPS(local_offset=9, location_formatting="dd")

    while True:
        gps.update_gps()

        sleep(0.5)
