import os
import time
import argparse
import math
from datetime import datetime
from serial_sonar import SerialSonarRead
from serial_gnss import SerialGnssRead
from i2c_imu import ImuRead

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-pg", "--port_gnss", default='/dev/ttyACM0',
                    help="Specification of serial communication port (eg. /dev/ttyACM0)")
    ap.add_argument("-ps", "--port_sonar", default='/dev/ttyUSB0',
                    help="Specification of serial communication port (eg. /dev/ttyUSB0)")
    ap.add_argument("-bg", "--baud_gnss", default=38400,
                    help="Serial communication baudrate (default 38400)")
    ap.add_argument("-bs", "--baud_sonar", default=115200,
                    help="Serial communication baudrate (default 115200)")
    ap.add_argument("-d", "--directory", default="measure_folder",
                    help='The name of the folder where the data will be stored (default "measure_folder")')
    ap.add_argument("-f", "--frequency", default=1,
                    help="Frequency of reading data (default 1 second)")
    ap.add_argument("-lg", "--length", default=2,
                    help="Length between GNSS and SONAR (default 1.5 m)")
    args = ap.parse_args()

    # inicializate meas. equipments
    sonar = SerialSonarRead(args.port_sonar, args.baud_sonar)
    gnss = SerialGnssRead(args.port_gnss, args.baud_gnss)
    imu = ImuRead()

    # start read data in separate threads
    sonar.start()
    gnss.start()
    imu.start()

    # create file in folder
    _file_name = os.path.join(args.directory, datetime.utcnow().strftime(
        "%d_%B_%Y_%H-%M-%S"))

    f_raw = open(_file_name + "_raw.csv", "w")
    f_cor = open(_file_name + "_cor.csv", "w")

    # write header description to files
    f_raw.write(
        "timestamp,lat[deg],lon[deg],hel[m],fix_status,depth_raw[m],temperature[C°],pitch[rad],roll[rad]\n")
    f_cor.write("timestamp,Y_jtsk[m],X_jtsk[m],H_bpv[m],fix_status\n")

    TIME_DELAY = 1 / int(args.frequency)

    try:
        while True:
            try:
                # correct depth by IMU
                # depthX = gnss.x_jtsk + sonar.depth * math.sin(imu.roll) * math.tan(imu.heading)
                # depthY = gnss.y_jtsk + sonar.depth * math.sin(imu.pitch) * math.tan(imu.heading)
                depthZ = gnss.h_bpv - args.length - sonar.depth * math.cos(imu.roll) * math.cos(imu.pitch)

                f_raw.write("{},{:.14f},{:.14f},{:.4f},{},{:.4f},{:.2f},{:.14f},{:.14f}\n".format(gnss.timestamp, gnss.lat,
                            gnss.lon, gnss.alt, gnss.fix_status, sonar.depth, sonar.tempature, imu.pitch, imu.roll))
                print(sonar.tempature)
                f_cor.write("{},{:.4f},{:.4f},{:.4f},{}\n".format(
                    gnss.timestamp, gnss.y_jtsk, gnss.x_jtsk, depthZ, gnss.fix_status))
            except Exception as err:
                pass

            time.sleep(TIME_DELAY)

    except (KeyboardInterrupt, SystemExit):
        print("Measure app was stopped by user")

    # stop threads
    sonar.stop()
    gnss.stop()

    # close file
    f_raw.close()
    f_cor.close()
