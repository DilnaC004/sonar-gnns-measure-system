# sonar-gnns-measure-system

instalation of necessary packages :

```bash
pip3 install -r requirements.txt
```

parameters :

```bash
-h  | --help               : help
-pg | --port_gnss          : Specification of GNSS serial communication port (eg. /dev/ttyACM0)
-ps | --port_sonar         : Specification of Sonar serial communication port (eg. /dev/ttyUSB0)
-bg | --baud_gnss          : Gnss communication baudrate (default 38400)
-bg | --baud_sonar         : Sonar communication baudrate (default 115200)
-d  | --directory          : The name of the folder where the data will be stored (default "measure_folder")
-f  | --frequency          : Frequency of reading data (default 1 second)
-lg | --lenght             : Length between GNSS and SONAR (ARP-0.056 + cover-0.12 + staff-2.00 + sonar-0.12 m)
-bp | --bias_pitch         : IMU bias calibration pitch (default 0.0)
-br | --bias_roll          : IMU bias calibration roll (default 0.0)
-ul | --server_url         : Display server address (default localhost:5000)
-nt | --ntrip_config_path  : NTRIP configuration path :: json_data example ->
                                {
                                    "ntrip_server": "czeposr.cuzk.cz",
                                    "ntrip_port": 2101,
                                    "ntrip_mountpoint": "CPRG3-MSM",
                                    "ntrip_user": "#####",
                                    "ntrip_password": "#####",
                                    "ntrip_is_virtual": false,
                                }
```

**Default run script :**

```bash
python3 main.py
```

**Spec. conf run script :**

```bash
python3 main.py -pg /dev/ttyACM1 -d /testing_dir
```

**TODO:**

- testing
- recalculation depth based on water temperature
