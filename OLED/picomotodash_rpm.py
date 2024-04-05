# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard RPM
"""

__author__ = "Salvatore La Bua"


from machine import Pin, Timer
from utime import ticks_us

pin = 22
PWM2RPM_FACTOR = 10


class RPM:

    def __init__(self, pin=pin, factor=PWM2RPM_FACTOR, autostart=False):

        self.pwm = Pin(pin, Pin.IN, Pin.PULL_DOWN)  # RPM pwm

        self.curr_interrupt = ticks_us()
        self.prev_interrupt = ticks_us()
        self.durations = []

        self.RPM_ESTIMATE = 0
        self.factor = factor

        self.n_repeats = 1
        self.duty = 50

        self.timeout = False
        self.timeout_max = 1000

        self.timer = Timer()

        if autostart:
            self.start()

    def start(self):
        self.pwm.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self.estimate,
            # priority=2,
            # hard=True,
        )
        self.timer.init(
            freq=(1 / 1),
            mode=Timer.PERIODIC,
            callback=self.set_timeout,
        )

    def stop(self):
        self.pwm.irq(handler=None)
        self.timer.deinit()

    def reset(self):
        self.curr_interrupt = ticks_us()
        self.prev_interrupt = ticks_us()
        self.durations = []

        self.RPM_ESTIMATE = 0
        self.duty = 50
        self.n_repeats = 1

        self.timeout = False

        self.start()

    def estimate(self, _):

        self.curr_interrupt = ticks_us()
        cycle_duration = self.curr_interrupt - self.prev_interrupt
        self.prev_interrupt = self.curr_interrupt

        if len(self.durations) > self.n_repeats:
            self.durations.pop(0)
        self.durations.append(cycle_duration)
        duration_avg = sum(self.durations) / len(self.durations)

        freq = 1000000 / duration_avg

        repeat_factor = ((50 - 20) / (1500 - 150)) * freq + (  # y = mx + q
            50 - ((50 - 20) / (1500 - 150) * 1500)  # magic numbers
        )
        self.n_repeats = (
            int(freq / repeat_factor) if int(freq / repeat_factor) != 0 else 1
        )

        self.RPM_ESTIMATE = freq * self.factor

    def set_timeout(self, _):
        if ticks_us() - self.curr_interrupt > self.timeout_max:
            self.stop()
            self.timeout = True

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass


if __name__ == "__main__":
    from machine import PWM
    from utime import sleep

    pwm2 = PWM(Pin(2))
    pwm2.freq(802)
    pwm2.duty_u16(32768)

    rpm = RPM(pin=pin, factor=PWM2RPM_FACTOR, autostart=True)

    while True:
        if not rpm.timeout and rpm.RPM_ESTIMATE > 0:
            print(rpm.n_repeats, rpm.RPM_ESTIMATE)
        else:
            # rpm.stop()
            print("TIMEOUT", rpm.RPM_ESTIMATE)
            sleep(0.5)
            rpm.reset()
            # rpm.start()

        sleep(0.02)
