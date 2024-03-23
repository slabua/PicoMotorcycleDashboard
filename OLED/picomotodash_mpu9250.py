# -*- coding: utf-8 -*-
"""Pico Motorcycle Dashboard MPU
"""

__author__ = "Salvatore La Bua"


from machine import I2C, Pin
from math import atan2, copysign, cos, sin, sqrt
from mpu6500 import MPU6500
from mpu9250 import MPU9250
from ujson import dump, load
from utime import sleep, ticks_diff, ticks_us


# MPU = 0x68
id = 1
sda = Pin(6)
scl = Pin(7)

RAD2DEG = 180 / 3.1415
DEG2RAD = 3.1415 / 180


class MPU:

    def __init__(
        self,
        id=id,
        scl=scl,
        sda=sda,
        freq=400000,
        calib_ag=True,
        tiltcomp=True,
        truenorth=True,
        parent=None,
    ):

        print("Initialising MPU9250...")

        i2c = I2C(id=id, scl=scl, sda=sda, freq=freq)
        # print(i2c.scan())

        mpu6500 = MPU6500(i2c=i2c, accel_sf=1, gyro_sf=1)
        self.mpu = MPU9250(i2c=i2c, mpu6500=mpu6500)

        print("Calibrating Magnetometer...")
        self.mpu.ak8963.calibrate(count=100)
        print("Calibration Completed.")

        self.imu = []

        self.dt = 0
        self.comp_pc = 0.99
        self.lowpass_pc = 0.8

        self.aXerr = 0
        self.aYerr = 0
        self.aZerr = 0
        self.gXerr = 0
        self.gYerr = 0
        self.gZerr = 0

        self.gyro_roll = None
        self.gyro_pitch = None
        self.gyro_yaw = 0

        self.roll_bias = 0.0
        self.pitch_bias = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.comp_roll = None
        self.comp_pitch = None
        self.lowpass_roll = None
        self.lowpass_pitch = None
        self.lowpass_mx = 0.0
        self.lowpass_my = 0.0
        self.tiltcomp = tiltcomp
        self.truenorth = truenorth
        self.heading = 0

        # https://www.magnetic-declination.com/Japan/Kyoto/1340633.html
        self.declination = -8.12  # Kyoto

        if calib_ag:
            self.calib_ag()

        self.start = ticks_us()

        self.imu = self.update_mpu()
        self.roll_bias = self.roll
        self.pitch_bias = self.pitch

        print("MPU9250 Initialised.")

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

            self.aZerr += 1  # 9.80665

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

    def lowpass(self, alpha, new_value, old_value):
        return (alpha * new_value) + (1.0 - alpha) * old_value

    def update_mpu(self):
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

        self.roll, self.pitch = self.get_roll_pitch_my(alpha=self.comp_pc)
        self.heading = self.get_heading(
            alpha=self.lowpass_pc, tiltcomp=self.tiltcomp, truenorth=self.truenorth
        )

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

    def get_roll_pitch_my(self, alpha=1.0):
        now = ticks_us()
        self.dt = ticks_diff(now, self.start) / 1000000
        self.start = now

        # Read sensor data
        # TODO Fix sign for both roll and pitch
        ax = self.imu[0]
        ay = self.imu[1]
        az = self.imu[2]

        gx = self.imu[3]
        gy = self.imu[4]
        gz = self.imu[5]

        # Calculate gyro rate [deg/sec]
        gyroXRate = gx  # / 0.017453292519943
        gyroYRate = gy  # / 0.017453292519943
        gyroZRate = gz  # / 0.017453292519943

        # Calculate gyro angle [deg]
        gyroXAngle = gyroXRate * self.dt
        gyroYAngle = gyroYRate * self.dt
        gyroZAngle = gyroZRate * self.dt * DEG2RAD

        # Calculate roll and pitch
        roll = atan2(ay, sqrt((ax * ax) + (az * az)))
        pitch = atan2(-ax, sqrt((ay * ay) + (az * az)))

        roll -= pitch * sin(gyroZAngle) * RAD2DEG
        pitch += roll * sin(gyroZAngle) * RAD2DEG

        # Calculate composite angle
        if self.comp_roll is None:
            self.comp_roll = roll
        else:
            self.comp_roll = alpha * (self.comp_roll + gyroXAngle) + (1 - alpha) * roll

        if self.comp_pitch is None:
            self.comp_pitch = pitch
        else:
            self.comp_pitch = (
                alpha * (self.comp_pitch + gyroYAngle) + (1 - alpha) * pitch
            )

            # print("roll", roll, "pitch", pitch)
            # #print("roll", roll, "pitch", pitch, "c_roll", self.comp_roll, "c_pitch", self.comp_pitch)
            # print("dt", dt, "roll", roll, "g_roll", gyro_roll, "c_roll", comp_roll)
            # print("pitch", pitch, "c_pitch", comp_pitch)
            # print(gyroXAngle, gyroYAngle, gyroZAngle)
            # print(gyro_yaw)

        if self.lowpass_roll is None:
            self.lowpass_roll = self.comp_roll
        else:
            self.lowpass_roll = self.lowpass(
                self.lowpass_pc, self.comp_roll, self.lowpass_roll
            )
        if self.lowpass_pitch is None:
            self.lowpass_pitch = self.comp_pitch
        else:
            self.lowpass_pitch = self.lowpass(
                self.lowpass_pc, self.comp_pitch, self.lowpass_pitch
            )

        return self.lowpass_roll, self.lowpass_pitch

    def get_heading(self, alpha=1.0, tiltcomp=False, truenorth=True):

        mx = self.imu[6]
        my = self.imu[7]
        mz = self.imu[8]

        # TODO Fix this block
        if tiltcomp:
            m_roll = self.comp_roll * DEG2RAD
            m_pitch = self.comp_pitch * DEG2RAD

            mx = (
                mx * cos(m_pitch)
                + my * sin(m_roll) * sin(m_pitch)
                - mz * cos(m_roll) * sin(m_pitch)
            )
            my = my * cos(m_roll) + mz * sin(m_roll)

        self.lowpass_mx = self.lowpass(alpha, mx, self.lowpass_mx)
        self.lowpass_my = self.lowpass(alpha, my, self.lowpass_my)

        # Calculate heading in radians and North to zero
        heading = 90 - atan2(self.lowpass_my, self.lowpass_mx) * RAD2DEG

        # Adjust for negative values
        # if heading_deg < 0:
        #     heading_deg += 360
        declination = self.declination if truenorth else 0
        heading = (heading + declination + 360) % 360
        heading = (180 - heading) % 360

        return heading

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
            # print(mpu9250.update())
            mpu9250.update_mpu()

            # pitch, roll, heading = mpu9250.get_roll_pitch_v1(mpu9250.lowpass_pc)
            print("roll " + str(mpu9250.roll))
            print("pitch " + str(mpu9250.pitch))
            print("heading " + str(mpu9250.heading))

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
            sleep(0.1)

    except KeyboardInterrupt:
        exit()
