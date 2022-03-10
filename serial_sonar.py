import serial
import time
import string
import os
import re
import threading

class SerialSonarRead(threading.Thread):
    def __init__(self, com_port='/dev/ttyUSB0', baudrate=115200):
        super().__init__()
        self._stop_event = threading.Event()
        self.serial_object = serial.Serial(com_port, int(baudrate))
        self.depth = ""
        self.tempature = ""

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

        splited_data = serial_data.split(",")

        if splited_data[0] == "$GPDPT":
            self.depth = float(splited_data[1])
            
        elif splited_data[0] == "$GPMTW":
            self.tempature = float(splited_data[1])
                
    def stop(self):
        self._stop_event.set()
        self.serial_object.close()

    def stopped(self):
        return self._stop_event.is_set()

