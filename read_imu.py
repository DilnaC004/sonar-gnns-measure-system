# coding: utf-8
## @package faboMPU9250
#  This is a library for the FaBo 9AXIS I2C Brick.
#
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

import FaBo9Axis_MPU9250
import time
import sys
import math

mpu9250 = FaBo9Axis_MPU9250.MPU9250()

accel = mpu9250.readAccel()
gyro = mpu9250.readGyro()
mag = mpu9250.readMagnet()

magDeclination = 0.082321

pitch = math.atan2( accel['y'] , math.sqrt( pow(accel['x'],2) + pow(accel['z'],2) ) )
roll = math.atan2( accel['x'] , math.sqrt( pow(accel['y'],2) + pow(accel['z'],2) ) )
heading = math.atan2(mag['y'],mag['x']) + magDeclination
start = time.time()

try:
    while True:
        accel = mpu9250.readAccel()
        gyro = mpu9250.readGyro()
        mag = mpu9250.readMagnet()

        dt = time.time() - start
        start = time.time()
        
        pitchAcc = math.atan2( accel['y'] , math.sqrt( pow(accel['x'],2) + pow(accel['z'],2) ) )
        rollAcc = math.atan2( accel['x'] , math.sqrt( pow(accel['y'],2) + pow(accel['z'],2) ) )
        headingMag = math.atan2(mag['y'],mag['x']) + magDeclination
        
        pitch = 0.7*(pitch + gyro['y']/180*math.pi*dt) + 0.3*pitchAcc
        roll = 0.7*(roll + gyro['x']/180*math.pi*dt) + 0.3*rollAcc
        heading = 0.7*(heading + gyro['z']/180*math.pi*dt) + 0.3*headingMag
        
        print(" pitch = " , ( pitch ))
        print(" roll = " , ( roll ))
        print(" heading = " , ( headingMag ))
        print()


except KeyboardInterrupt:
    sys.exit()
