# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard RPM
"""

__author__ = "Salvatore La Bua"


from machine import Pin
from utime import sleep_us, ticks_us

pin = 22
PWM2RPM_FACTOR = 10


class RPM:

    def __init__(self, pin=pin, factor=PWM2RPM_FACTOR):

        self.pwm = Pin(pin, Pin.IN, Pin.PULL_DOWN)  # RPM pwm

        self.RPM_ESTIMATE = 0
        self.factor = factor

        self.n_repeats = 1
        self.duty = 50

        self.timeout = False
        self.timeout_count = 1000

    def reset(self):
        self.RPM_ESTIMATE = 0
        self.duty = 50
        self.n_repeats = 1
        self.timeout = False

    def estimate_rpm(self):

        durations = []
        if self.pwm.value() == 1:
            cycle_start = ticks_us()

            for _ in range(self.n_repeats):
                count = 0
                d_start = ticks_us()
                while self.pwm.value() == 1:
                    count += 1
                    sleep_us(100)
                    if count > self.timeout_count:
                        self.timeout = True
                        return
                durations.append(ticks_us() - d_start)
                while self.pwm.value() == 0:
                    count += 1
                    sleep_us(100)
                    if count > self.timeout_count:
                        self.timeout = True
                        return
            cycle_stop = ticks_us()
            cycle_duration = cycle_stop - cycle_start
            cycle_avg = cycle_duration / self.n_repeats
            freq = 1000000 / cycle_avg
            duration_avg = sum(durations) / len(durations)

            repeat_factor = ((50 - 20) / (1500 - 150)) * freq + (  # y = mx + q
                50 - ((50 - 20) / (1500 - 150) * 1500)
            )
            self.n_repeats = (
                int((freq) / repeat_factor) if int((freq) / repeat_factor) != 0 else 1
            )
            self.duty = (duration_avg / cycle_avg) * 100
            self.RPM_ESTIMATE = round(freq * self.factor)

            # print("RPM: {:.2f}".format(self.RPM_ESTIMATE), self.n_repeats, repeat_factor)

        else:
            count = 0
            while self.pwm.value() == 0:
                count += 1
                sleep_us(100)
                if count > self.timeout_count:
                    self.timeout = True
                    return

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass


if __name__ == "__main__":
    from machine import PWM
    from utime import sleep

    pwm2 = PWM(Pin(2))
    pwm2.freq(800)
    pwm2.duty_u16(32768)

    rpm = RPM(pin=pin, factor=PWM2RPM_FACTOR)

    while True:
        _ = rpm.estimate_rpm()
        if not rpm.timeout:
            print(rpm.RPM_ESTIMATE)
        else:
            print("TIMEOUT", rpm.RPM_ESTIMATE)
            sleep(0.5)
            rpm.reset()

        sleep(0.02)
