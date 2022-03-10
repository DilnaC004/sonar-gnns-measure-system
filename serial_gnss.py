import serial
import time
import string
import os
import re
import threading
import krovak5 # no path!!!!!!
import pynmea2 # no path!!!!!!

class SerialSonarRead(threading.Thread):
    def __init__(self, com_port='/dev/ttyAMC0', baudrate=38400):
        super().__init__()
        self._stop_event = threading.Event()
        self.serial_object = serial.Serial(com_port, int(baudrate))
        self.x = ""
        self.y = ""
        self.h = ""
        self.timeStamp = ""

    def run(self):
        '''
        The method that actually gets data from the port
        '''
        while not self.stopped():
            serial_data = self.serial_object.readline()

            try:

                self.get_NMEA_parse(
                    serial_data.decode("ascii", errors="replace"))


            except Exception as error:
                print('Some error in data: ', serial_data)
                print(error)
                
    def get_NMEA_parse(self, serial_data):

        gnss_nmea = pynmea2.parse(serial_data, check=True)

        self.timeStamp = gnss_nmea.timestamp

        self.x, self.y, self.h = krovak5.etrs_jtsk05(gnss_nmea.longitude, gnss_nmea.latitude, gnss_nmea.altitude)
                
    def stop(self):
        self._stop_event.set()
        self.serial_object.close()

    def stopped(self):
        return self._stop_event.is_set()

