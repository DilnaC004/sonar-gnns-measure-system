import serial
import pynmea2
import threading
import logging

from krovak05 import Transformation

log = logging.getLogger(__name__)


class SerialGnssRead(threading.Thread):
    def __init__(self, com_port='/dev/ttyAMC0', baudrate=38400):
        super().__init__()
        self._stop_event = threading.Event()
        self.serial_object = serial.Serial(com_port, int(baudrate))
        self.tranformation = Transformation()

        # properties
        self.lat = None
        self.lon = None
        self.alt = None
        self.y_jtsk = None
        self.x_jtsk = None
        self.h_bpv = None
        self.fix_status = None
        self.timestamp = None
        self.last_gga = None

    def run(self) -> None:
        '''
        The method that actually gets data from the port
        '''
        while not self.stopped():
            serial_data = self.serial_object.readline()

            try:
                self.get_NMEA_parse(
                    serial_data.decode("ascii", errors="replace"))

            except Exception:
                log.exception(f"Some error in data: {serial_data}")

    def get_NMEA_parse(self, serial_data) -> None:
        """Parse NMEA data from GNSS

        Args:
            serial_data (str): string line from serial
        """

        gnss_nmea = pynmea2.parse(serial_data, check=True)

        # process only GGA data, YET
        if gnss_nmea.sentence_type == "GGA":

            self.timestamp = gnss_nmea.timestamp
            self.fix_status = gnss_nmea.gps_qual
            self.lat = gnss_nmea.latitude
            self.lon = gnss_nmea.longitude
            self.last_gga = serial_data

            # elipsoidic height -- in GGA message is height about sea level
            # H_el = H_sea + Geo_separation
            self.alt = gnss_nmea.altitude
            self.hel = gnss_nmea.altitude + float(gnss_nmea.geo_sep)

            self.y_jtsk, self.x_jtsk, self.h_bpv = self.tranformation.etrs_jtsk(
                self.lat, self.lon, self.hel)

    def stop(self) -> None:
        """Stop thread
        """
        self._stop_event.set()
        self.serial_object.close()

    def stopped(self) -> bool:
        """Check if thread was stopped

        Returns:
            bool: 
        """
        return self._stop_event.is_set()
