# sonar-gnns-measure-system

instalation of necessary packages :

```bash
pip install -r requirements.txt
```

parameters :

```bash
-h                 : help
-pg | --port_gnss  : Specification of GNSS serial communication port (eg. /dev/ttyACM0)
-ps | --port_sonar : Specification of Sonar serial communication port (eg. /dev/ttyUSB0)
-bg | --baud_gnss  : Gnss communication baudrate (default 38400)
-bg | --baud_sonar : Sonar communication baudrate (default 115200)
-d  | --directory  : The name of the folder where the data will be stored (default "measure_folder")
-f  | --frequency  : Frequency of reading data (default 1 second)
```

**Default run script :**

```bash
python3 main.py
```

**Spec. conf run script :**

```bash
python3 main.py -pg /dev/ttyACM1 -d /testing_dir
```
