# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard OLED
"""

__author__ = "Salvatore La Bua"


from machine import I2C, Pin
from math import atan2, copysign, sqrt
from mpu9250 import MPU9250
from ujson import dump, load
from utime import sleep


# MPU = 0x68
id = 1
sda = Pin(6)
scl = Pin(7)

RAD2DEG = 180 / 3.1415


class MPU:

    def __init__(
        self, id=id, scl=scl, sda=sda, freq=400000, calib_ag=True, parent=None
    ):

        print("Initialising MPU9250...")

        i2c = I2C(id=id, scl=scl, sda=sda, freq=freq)

        # print(i2c.scan())
        self.mpu = MPU9250(i2c)

        print("Calibrating Magnetometer...")
        self.mpu.ak8963.calibrate(count=100)
        print("Calibration Completed.")

        self.imu = []

        self.dt = 0
        self.lowpass_pc = 0.8
        # self.comp_pc = 0.99

        self.aXerr = 0
        self.aYerr = 0
        self.aZerr = 0
        self.gXerr = 0
        self.gYerr = 0
        self.gZerr = 0

        # self.comp_roll = None
        # self.comp_pitch = None
        # self.gyro_roll = None
        # self.gyro_pitch = None
        # self.gyro_yaw = 0

        self.roll_bias = 0.0
        self.pitch_bias = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.comp_mx = 0.0
        self.comp_my = 0.0
        self.heading = 0

        # https://www.magnetic-declination.com/Japan/Kyoto/1340633.html
        self.declination = -8.12  # Kyoto

        if calib_ag:
            self.calib_ag()

        self.imu = self.update()
        self.roll_bias = self.roll
        self.pitch_bias = self.pitch

        # self.start = ticks_us()

        print("MPU6050 Initialised.")

    def calib_ag(self, period=0.02, n_samples=1000):
        print("Running Accel/Gyro Calibration...")

        try:
            with open("calib.json", "r") as calib_file:
                self.read_calib(calib_file)

        except OSError:
            print("Calibration file not found.")
            print("Starting Calibration...")

            for _ in range(n_samples):
                ax, ay, az = self.mpu.acceleration
                gx, gy, gz = self.mpu.gyro

                self.aXerr += ax
                self.aYerr += ay
                self.aZerr += az
                self.gXerr += gx
                self.gYerr += gy
                self.gZerr += gz

                sleep(period)

            self.aXerr /= n_samples
            self.aYerr /= n_samples
            self.aZerr /= n_samples
            self.gXerr /= n_samples
            self.gYerr /= n_samples
            self.gZerr /= n_samples

            self.aZerr += 9.80665

            print("Calibration errors:")
            print(
                self.aXerr,
                "\t",
                self.aYerr,
                "\t",
                self.aZerr,
                "\t",
                self.gXerr,
                "\t",
                self.gYerr,
                "\t",
                self.gZerr,
            )

            self.write_calib()

        print("Calibration Complete.")

    def read_calib(self, calib_file):
        print("Reading calibration file...")

        calib = load(calib_file)

        print("Calibration file found.")
        print("Reading calibration data...")

        self.aXerr = calib["aXerr"]
        self.aYerr = calib["aYerr"]
        self.aZerr = calib["aZerr"]
        self.gXerr = calib["gXerr"]
        self.gYerr = calib["gYerr"]
        self.gZerr = calib["gZerr"]

    def write_calib(self):
        print("Writing calibration...")
        calib = {
            "aXerr": self.aXerr,
            "aYerr": self.aYerr,
            "aZerr": self.aZerr,
            "gXerr": self.gXerr,
            "gYerr": self.gYerr,
            "gZerr": self.gZerr,
        }
        with open("calib.json", "w") as calib_file:
            dump(calib, calib_file)
        print("Calibration file written.")

    def low_pass(self, alpha, new_value: float, old_value):
        return (alpha * new_value) + (1.0 - alpha) * old_value

    def update(self):
        a = self.mpu.acceleration
        g = self.mpu.gyro
        m = self.mpu.magnetic

        self.imu = [
            a[0] - self.aXerr,
            a[1] - self.aYerr,
            a[2] - self.aZerr,
            g[0] - self.gXerr,
            g[1] - self.gYerr,
            g[2] - self.gZerr,
            m[0],
            m[1],
            m[2],
        ]

        self.roll, self.pitch = self.get_roll_pitch()
        self.heading = self.get_heading(self.lowpass_pc)

        return self.imu

    def get_roll_pitch(self) -> float:
        """Returns the readings from the sensor"""

        ax = self.imu[0]
        ay = self.imu[1]
        az = self.imu[2]

        roll = atan2(-ax, sqrt((ay * ay) + (az * az))) * RAD2DEG
        pitch = (
            atan2(az, copysign(ay, ay) * sqrt((0.01 * ax * ax) + (ay * ay))) * RAD2DEG
        )

        roll -= self.roll_bias
        pitch -= self.pitch_bias

        return roll, pitch

    def get_heading(self, alpha=1.0):

        mx = self.imu[6]
        my = self.imu[7]

        self.comp_mx = self.low_pass(alpha, mx, self.comp_mx)
        self.comp_my = self.low_pass(alpha, my, self.comp_my)

        heading = 90 - atan2(self.comp_my, self.comp_mx) * RAD2DEG

        # if heading_deg < 0:
        #     heading_deg += 360
        heading = (heading + self.declination + 360) % 360
        heading = (180 - heading) % 360

        return heading

    # def get_roll_pitch_v2(self, alpha=1.0):

    #     now = ticks_us()
    #     self.dt = ticks_diff(now, self.start) / 1000000
    #     self.start = now

    #     # Read sensor data
    #     ax, ay, az, gx, gy, gz, mx, my, mz = self.get_agm()

    #     # Calculate gyro rate [deg/sec]
    #     gyroXRate = gx / 0.017453292519943
    #     gyroYRate = gy / 0.017453292519943
    #     gyroZRate = gz / 0.017453292519943

    #     # Calculate gyro angle [deg]
    #     gyroXAngle = gyroXRate * self.dt
    #     gyroYAngle = gyroYRate * self.dt
    #     gyroZAngle = gyroZRate * self.dt

    #     # Calculate roll and pitch
    #     roll = atan2(ay, sqrt((ax * ax) + (az * az))) * RAD2DEG
    #     pitch = atan2(-ax, sqrt((ay * ay) + (az * az))) * RAD2DEG

    #     roll -= pitch * sin(gyroZAngle)
    #     pitch += roll * sin(gyroZAngle)

    #     # Calculate composite angle
    #     if self.comp_roll is None:
    #         self.comp_roll = roll
    #     else:
    #         self.comp_roll = alpha * (self.comp_roll + gyroXAngle) + (1 - alpha) * roll

    #     if self.comp_pitch is None:
    #         self.comp_pitch = pitch
    #     else:
    #         self.comp_pitch = (
    #             alpha * (self.comp_pitch + gyroYAngle) + (1 - alpha) * pitch
    #         )

    #     # print("roll", roll, "pitch", pitch)
    #     # #print("roll", roll, "pitch", pitch, "c_roll", self.comp_roll, "c_pitch", self.comp_pitch)
    #     # print("dt", dt, "roll", roll, "g_roll", gyro_roll, "c_roll", comp_roll)
    #     # print("pitch", pitch, "c_pitch", comp_pitch)
    #     # print(gyroXAngle, gyroYAngle, gyroZAngle)
    #     # print(gyro_yaw)

    #     return self.comp_roll, self.comp_pitch

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass


if __name__ == "__main__":
    mpu9250 = MPU()

    try:
        while True:
            # print(
            #     "\r\n /-------------------------------------------------------------/ \r\n"
            # )
            mpu9250.update()

            # pitch, roll, heading = mpu9250.get_roll_pitch_v1(mpu9250.lowpass_pc)
            # print(mpu9250.roll, mpu9250.pitch)
            print("heading", mpu9250.heading)

            # pitch, roll = mpu9250.get_roll_pitch_v2(mpu9250.comp_pc)
            # print(mpu9250.get_roll_pitch_v3(mpu9250.comp_pc))

            # print(
            #     "\r\n /-------------------------------------------------------------/ \r\n"
            # )
            # print(
            #     "\r\n Roll = %.2f , Pitch = %.2f , Yaw = %.2f\r\n"
            #     % (roll, pitch, yaw)
            #     # "Roll: "
            #     # + str(roll)
            #     # + "\tPitch: "
            #     # + str(pitch)
            #     # "Yaw: "
            #     # + str(scaled_yaw)
            # )
            # print(
            #     "\r\nAcceleration:  X = %d , Y = %d , Z = %d\r\n"
            #     % (Accel[0], Accel[1], Accel[2])
            # )
            # print(
            #     "\r\nGyroscope:     X = %d , Y = %d , Z = %d\r\n"
            #     % (Gyro[0], Gyro[1], Gyro[2])
            # )
            # print(
            #     "\r\nMagnetic:      X = %d , Y = %d , Z = %d"
            #     % (
            #         (Mag[1]),  # * 10 * 32760.0 / 4912.0),  # + 32760.0,
            #         (-Mag[0]),  # * 10 * 32760.0 / 4912.0),  # + 32760.0,
            #         (Mag[2]),  # * 10 * 32760.0 / 4912.0),  # + 32760.0,
            #         # (-((Mag[0] - 4912.0))),
            #         # ((Mag[1] + 4912.0)),
            #         # (-((Mag[2] - 4912.0))),
            #     )
            # )
            sleep(0.05)

    except KeyboardInterrupt:
        exit()
