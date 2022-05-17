import FaBo9Axis_MPU9250
import time
import sys
import math
import threading


class ImuRead(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.mpu9250 = FaBo9Axis_MPU9250.MPU9250()

        accel = self.mpu9250.readAccel()
        # gyro = self.mpu9250.readGyro()
        # mag = self.mpu9250.readMagnet()

        self.pitch = math.atan2( accel['y'] , math.sqrt( pow(accel['x'],2) + pow(accel['z'],2) ) )
        self.roll = math.atan2( accel['x'] , math.sqrt( pow(accel['y'],2) + pow(accel['z'],2) ) )
        # self.heading = None
        self.start = time.time()


    def run(self):
        '''
        The method that actually gets data from the port
        '''
        while not self.stopped():
            accel = self.mpu9250.readAccel()
            gyro = self.mpu9250.readGyro()
            # mag = self.mpu9250.readMagnet()
            dt = time.time() - self.start
            self.start = time.time()
            
            try:
                pitchAcc = math.atan2( accel['y'] , math.sqrt( pow(accel['x'],2) + pow(accel['z'],2) ) )
                rollAcc = math.atan2( accel['x'] , math.sqrt( pow(accel['y'],2) + pow(accel['z'],2) ) )

                self.pitch = 0.7*(self.pitch + gyro['y']/180*math.pi*dt) + 0.3*pitchAcc
                self.roll = 0.7*(self.roll + gyro['x']/180*math.pi*dt) + 0.3*rollAcc
        
                print(" pitch = " , ( pitchAcc ))
                print(" roll = " , ( rollAcc ))
                print()

            except Exception as error:
                print(error)

    def stop(self) -> None:
        self._stop_event.set()
        self.serial_object.close()

    def stopped(self) -> bool:
        return self._stop_event.is_set()
