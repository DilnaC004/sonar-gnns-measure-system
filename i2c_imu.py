import time
import math
import threading
import logging
import FaBo9Axis_MPU9250


log = logging.getLogger(__name__)


class ImuRead(threading.Thread):
    def __init__(self, bias_pitch: float = 0.0, bias_roll: float = 0.0):
        super().__init__()
        self._stop_event = threading.Event()
        self.mpu9250 = FaBo9Axis_MPU9250.MPU9250()

        accel = self.mpu9250.readAccel()
        self.bias_pitch = bias_pitch
        self.bias_roll = bias_roll
        self.pitch = math.atan2(accel['y'], math.sqrt(
            pow(accel['x'], 2) + pow(accel['z'], 2))) + self.bias_pitch
        self.roll = math.atan2(accel['x'], math.sqrt(
            pow(accel['y'], 2) + pow(accel['z'], 2))) + self.bias_roll
        self.start_time = time.time()

    def run(self):
        '''
        The method that actually gets data from the port
        '''
        while not self.stopped():
            accel = self.mpu9250.readAccel()
            gyro = self.mpu9250.readGyro()
            dt = time.time() - self.start_time
            self.start_time = time.time()

            try:
                pitchAcc = math.atan2(accel['y'], math.sqrt(
                    pow(accel['x'], 2) + pow(accel['z'], 2))) + self.bias_pitch
                rollAcc = math.atan2(accel['x'], math.sqrt(
                    pow(accel['y'], 2) + pow(accel['z'], 2))) + self.bias_roll

                self.pitch = 0.7 * \
                    (self.pitch + gyro['y'] / 180 *
                     math.pi * dt) + 0.3 * pitchAcc
                self.roll = 0.7 * \
                    (self.roll + gyro['x'] / 180 *
                     math.pi * dt) + 0.3 * rollAcc

                log.debug(
                    f"pith_acc = {pitchAcc:.5f}\nroll_acc = {rollAcc:.5f}\n")

            except Exception as error:
                log.exception(error)

    def stop(self) -> None:
        self._stop_event.set()
        self.serial_object.close()

    def stopped(self) -> bool:
        return self._stop_event.is_set()
