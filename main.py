import os
import time
import math
import logging
import requests
import argparse
import setproctitle

from helper import get_size
from i2c_imu import ImuRead
from datetime import datetime
from ntrip_client import NtripClient
from serial_gnss import SerialGnssRead
from serial_sonar import SerialSonarRead

setproctitle.setproctitle("SonarMeasure")

actual_time = datetime.utcnow()
log_formatter = '%(asctime)s %(name)s %(message)s'

logging.basicConfig(filename=actual_time.strftime(
    "%Y_%m_%d__%H_%M_%S_log.txt"),
    format=log_formatter, level=logging.INFO)

for logger_name in [__name__, "i2c_imu", "serial_sonar", "serial_gnss", "ntrip_client", ]:
    logging.getLogger(logger_name).setLevel(logging.INFO)

log = logging.getLogger(__name__)

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
    ap.add_argument("-lg", "--length", default=0.056 + 0.12 + 2 + 0.12,
                    help="Length between GNSS and SONAR (ARP-0.056 + cover-0.12 + staff-2.00 + sonar-0.12 m)")
    ap.add_argument("-bp", "--bias_pitch", default=0.0,
                    help="IMU bias calibration pitch (default 0.0)")
    ap.add_argument("-br", "--bias_roll", default=0.0,
                    help="IMU bias calibration roll (default 0.0)")
    ap.add_argument("-ul", "--server_url", default='http://127.0.0.1:5000/send_data',
                    help="Display server address (default http://127.0.0.1:5000/send_data)")
    ap.add_argument("-nt", "--ntrip_config_path", default='',
                    help="NTRIP configuration path")
    args = ap.parse_args()

    # inicializate meas. equipments
    sonar = SerialSonarRead(args.port_sonar, args.baud_sonar)
    gnss = SerialGnssRead(args.port_gnss, args.baud_gnss)
    imu = ImuRead(args.bias_pitch, args.bias_roll)
    ntrip = NtripClient(args.ntrip_config_path, gnss)

    # start read data in separate threads
    sonar.start()
    gnss.start()
    ntrip.start()
    imu.start()

    # create file in folder
    _file_name = os.path.join(args.directory, datetime.utcnow().strftime(
        "%d_%B_%Y_%H-%M-%S"))

    file_name_raw = _file_name + "_raw.csv"
    file_name_cor = _file_name + "_cor.csv"

    with open(file_name_raw, "a") as f_raw, open(file_name_cor, "a") as f_cor:
        # write header description to files
        f_raw.write(
            "timestamp,lat[deg],lon[deg],hel[m],fix_status,depth_raw[m],temperature[C°],pitch[rad],roll[rad]\n")
        f_cor.write("timestamp,Y_jtsk[m],X_jtsk[m],H_bpv[m],fix_status\n")

    TIME_DELAY = 1 / int(args.frequency)

    try:
        while True:
            try:
                depthZ = gnss.h_bpv - \
                    (args.length + sonar.depth) * \
                    math.cos(imu.roll) * math.cos(imu.pitch)

                raw_file_size = get_size(file_name_raw)

                with open(file_name_raw, "a") as f_raw, open(file_name_cor, "a") as f_cor:
                    f_raw.write("{},{:.14f},{:.14f},{:.4f},{},{:.4f},{:.2f},{:.14f},{:.14f}\n".format(gnss.timestamp, gnss.lat,
                                gnss.lon, gnss.alt, gnss.fix_status, sonar.depth, sonar.tempature, imu.pitch, imu.roll))
                    f_cor.write("{},{:.4f},{:.4f},{:.4f},{}\n".format(
                        gnss.timestamp, gnss.y_jtsk, gnss.x_jtsk, depthZ, gnss.fix_status))

                # send data to displey server
                post_data = {
                    "JTSK-Y": f"{gnss.y_jtsk:.3f} m",
                    "JTSK-X": f"{gnss.x_jtsk:.3f} m",
                    "Atn. height": f"{gnss.h_bpv:.3f} m",
                    "Fix status": gnss.fix_status,
                    "Sonar depth": f"{sonar.depth:.3f} m",
                    "Sonar temp": f"{sonar.tempature:.1f} °C",
                    "Log. file": file_name_raw,
                    "File size": raw_file_size,
                }

                try:

                    response = requests.post(
                        args.server_url, json=post_data, timeout=0.5)

                    if not response.status_code == 200:
                        log.error(response.json())

                    # TODO:  read settings data from server
                except requests.exceptions.ConnectionError:
                    log.exception("cannot POST data")

            except Exception as err:
                pass

            time.sleep(TIME_DELAY)

    except (KeyboardInterrupt, SystemExit):
        log.exception("Measure app was stopped by user")

    # stop threads
    sonar.stop()
    imu.stop()
    ntrip.stop()
    gnss.stop()
