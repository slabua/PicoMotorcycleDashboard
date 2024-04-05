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

        # self.pulses = 0
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

    # def count(self, _):
    #     self.pulses += 1

    def set_timeout(self, _):
        # print("TIMEOUT_CHECK")
        # self.RPM_ESTIMATE = self.pulses * self.factor * 1
        # self.pulses = 0

        # state = disable_irq()
        # self.prev_interrupt = self.curr_interrupt

        if ticks_us() - self.curr_interrupt > self.timeout_max:
            self.stop()
            self.timeout = True

        # self.curr_interrupt = ticks_us()
        # enable_irq(state)

    # def estimate_rpm(self):

    #     durations = []
    #     if self.pwm.value() == 1:
    #         cycle_start = ticks_us()

    #         for _ in range(self.n_repeats):
    #             count = 0
    #             d_start = ticks_us()
    #             while self.pwm.value() == 1:
    #                 count += 1
    #                 sleep_us(100)
    #                 if count > self.timeout_max:
    #                     self.timeout = True
    #                     return
    #             durations.append(ticks_us() - d_start)
    #             while self.pwm.value() == 0:
    #                 count += 1
    #                 sleep_us(100)
    #                 if count > self.timeout_max:
    #                     self.timeout = True
    #                     return
    #         cycle_stop = ticks_us()
    #         cycle_duration = cycle_stop - cycle_start
    #         cycle_avg = cycle_duration / self.n_repeats
    #         freq = 1000000 / cycle_avg
    #         duration_avg = sum(durations) / len(durations)

    #         repeat_factor = ((50 - 20) / (1500 - 150)) * freq + (  # y = mx + q
    #             50 - ((50 - 20) / (1500 - 150) * 1500)
    #         )
    #         self.n_repeats = (
    #             int(freq / repeat_factor) if int(freq / repeat_factor) != 0 else 1
    #         )
    #         self.duty = duration_avg / cycle_avg * 100
    #         self.RPM_ESTIMATE = freq * self.factor

    #         # print("RPM: {:.2f}".format(self.RPM_ESTIMATE), self.n_repeats, repeat_factor)

    #     else:
    #         count = 0
    #         while self.pwm.value() == 0:
    #             count += 1
    #             sleep_us(100)
    #             if count > self.timeout_max:
    #                 self.timeout = True
    #                 return

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
        # rpm.estimate_rpm()
        if not rpm.timeout and rpm.RPM_ESTIMATE > 0:
            print(rpm.n_repeats, rpm.RPM_ESTIMATE)
        else:
            # rpm.stop()
            print("TIMEOUT", rpm.RPM_ESTIMATE)
            sleep(0.5)
            rpm.reset()
            # rpm.start()

        sleep(0.02)
