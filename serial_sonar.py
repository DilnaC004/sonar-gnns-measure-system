import serial
import threading


class SerialSonarRead(threading.Thread):
    def __init__(self, com_port='/dev/ttyUSB0', baudrate=115200):
        super().__init__()
        self._stop_event = threading.Event()
        self.serial_object = serial.Serial(com_port, int(baudrate))

        # properties
        self.depth = None
        self.depth_raw = None
        self.tempature = None

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

    def get_NMEA_parse(self, serial_data) -> None:
        """Parse NMEA data from sonar 

        Args:
            serial_data (str): string line from serial 
        """

        splited_data = serial_data.split(",")

        if splited_data[0] == "$GPDPT":
            self.depth = float(splited_data[1])

        elif splited_data[0] == "$GPMTW":
            self.tempature = float(splited_data[1])

        self.recalculate_depth()

    def recalculate_depth(self) -> None:
        """Recalculate depth based on slope and water temperature

        !!!Now not working!!!
        """

        # TODO: recalculate depth based on slope and water temperature

        self.depth = self.depth_raw

    def stop(self) -> None:
        self._stop_event.set()
        self.serial_object.close()

    def stopped(self) -> bool:
        return self._stop_event.is_set()
