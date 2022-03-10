import argparse
import time
import datatime #no path
from serial_sonar import SerialSonarRead
from serial_gnss import SerialGnssRead

if __name__ == "__main__":
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-g", "--port_gnss", default='/dev/ttyACM0',
                    help="Specification of serial communication port (eg. /dev/ttyACM0)")
    ap.add_argument("-s", "--port_sonar", default='/dev/ttyUSB0',
                    help="Specification of serial communication port (eg. /dev/ttyUSB0)")
    ap.add_argument("-bg", "--baudrateGnss", default=38400,
                    help="Serial communication baudrate (default 38400)")
    ap.add_argument("-bs", "--baudrateSonar", default=115200,
                    help="Serial communication baudrate (default 115200)")
    ap.add_argument("-d", "--directory", default="Test",
                    help='The name of the folder where the data will be stored (default "Test")')
    args = ap.parse_args()
    

	

    # call sonar
    sonar = SerialSonarRead(args.port_sonar,args.baudrateSonar)
    sonar.start()

    # call gnss
    gnss = SerialGnssRead(args.port_gnss,args.baudrateGnss)
    gnss.start()

    # create file in folder
    t = datatime.datetime.utcnow()
    file_name = t.strftime("%d_%B_%Y_%H-%M-%S") + "sonar.log"
    with open(file_name,"w") as f:
        while True:
            waterPoint = gnss.h + sonar.depth
            f.write(gnss.x + gnss.y + waterPoint + sonar.tempature)
            time.sleep(1)
