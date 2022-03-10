import os
import time
import argparse
from datetime import datetime
from serial_sonar import SerialSonarRead
from serial_gnss import SerialGnssRead

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
    args = ap.parse_args()

    # inicializate meas. equipments
    sonar = SerialSonarRead(args.port_sonar, args.baud_sonar)
    gnss = SerialGnssRead(args.port_gnss, args.baud_gnss)

    # start read data in separate threads
    sonar.start()
    gnss.start()

    # create file in folder
    _file_name = os.path.join(args.directory, datetime.utcnow().strftime(
        "%d_%B_%Y_%H-%M-%S"))

    f_raw = open(_file_name + "_raw.csv", "w")
    f_cor = open(_file_name + "_cor.csv", "w")

    # write header description to files
    f_raw.write(
        "timestamp,lat[deg],lon[deg],hel[m],fix_status,depth_raw[m],temperature[C°],inc_x[deg],inc_y[deg]\n")
    f_cor.write("timestamp,Y_jtsk[m],X_jtsk[m],H_bpv[m],fix_status\n")

    TIME_DELAY = 1 / int(args.frequency)

    try:
        while True:

            # TODO: add inclinations
            f_raw.write("{},{:.14f},{:.14f},{:.4f},{},{:.4f},{:.2f},None,None\n".format(gnss.timestamp, gnss.lat,
                        gnss.lon, gnss.hel, gnss.fix_status, sonar.depth_raw, sonar.tempature))
            f_cor.write("{},{:.4f},{:.4f},{:.4f},{}\n".format(
                gnss.timestamp, gnss.y_jtsk, gnss.x_jtsk, gnss.h_bpv - sonar.depth, gnss.fix_status))
            time.sleep(TIME_DELAY)

    except (KeyboardInterrupt, SystemExit):
        print("Measure app was stopped by user")

    # stop threads
    sonar.stop()
    gnss.stop()

    # close file
    f_raw.close()
    f_cor.close()
