import os
import json
import time
import socket
import serial
import base64
import logging
import threading

from datetime import datetime

log = logging.getLogger(__name__)

# "ntrip_mountpoint": "iMAX3C-MSM",

DEFAULT_CONFIG = {
    "ntrip_server": "czeposr.cuzk.cz",
    "ntrip_port": 2101,
    "ntrip_mountpoint": "CPRG3-MSM",
    "ntrip_user": "*****",
    "ntrip_password": "****",
    "ntrip_is_virtual": False,
}


class NtripClient(threading.Thread):
    def __init__(self, config_path: str = None, gnss=None) -> None:
        super().__init__()
        self._stop_event = threading.Event()

        if config_path is None or not os.path.exists(config_path):
            config = DEFAULT_CONFIG
        else:
            with open(config_path) as file:
                config = json.load(file)

        self._ntrip_server = config["ntrip_server"]
        self._ntrip_port = config["ntrip_port"]
        self._ntrip_mountpoint = config["ntrip_mountpoint"]
        self._ntrip_user = config["ntrip_user"]
        self._ntrip_password = config["ntrip_password"]
        self._is_virtual = config["ntrip_is_virtual"]
        self._gnss = gnss
        self._serial_port = None if self._gnss is None else self._gnss.serial_object

        log.debug('NTRIP imported')

    def run(self):

        while not self.stopped():
            try:
                log.info("Connecting to ntrip")
                self.connect_server()
            except Exception as er:
                logging.exception(er)

            time.sleep(2)

    def connect_server(self):
        if self._is_virtual and self._gnss.last_gga == "":
            logging.info("Waiting for valid GGA")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._ntrip_server, self._ntrip_port))
            s.sendall(self.get_server_connection_string())

            while not self.stopped():
                received_data = s.recv(1024)

                if not received_data:
                    log.info("Ntrip server disconnected")
                    break

                # check serial for debug output
                if type(self._serial_port) == serial.Serial:
                    self._serial_port.write(received_data)
                else:
                    log.info(received_data)

    def get_access_string(self):
        auth = "{}:{}".format(
            self._ntrip_user, self._ntrip_password).encode("utf-8")
        return base64.b64encode(auth).decode("utf-8")

    def get_server_connection_string(self):

        return ("GET /{} HTTP/1.0\r\n"
                "Host:{}\r\n"
                "User-Agent: NTRIPClient for pythonScript\r\n"
                "Authorization: Basic {}\r\n{}").format(self._ntrip_mountpoint, self._ntrip_server, self.get_access_string(), self._gnss.last_gga + "\r\n" if self._is_virtual else "\r\n").encode("utf-8")

    def stop(self) -> None:
        """Stop thread
        """
        self._stop_event.set()

    def stopped(self) -> bool:
        """Check if thread was stopped

        Returns:
            bool: 
        """
        return self._stop_event.is_set()


if __name__ == "__main__":

    """Testing NTRIP function"""

    config_path = "configuration.json"
    ntrip = NtripClient(config_path, None)
    start_time = datetime.now()

    try:
        ntrip.start()

        while (datetime.now() - start_time).total_seconds() < 20:
            print("WHILE::")
            time.sleep(1)

    except Exception as err:
        pass

    ntrip.stop()

    # ntrip.run()
