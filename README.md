# Riden
A python library for Riden RD6006-RD6018 power supplies

This is based on [Baldanos/rd6006](https://github.com/Baldanos/rd6006)

There's getters and setters for everything but M0-9 V/I/OVP/OCP.  
The `update` function will update `Riden` class properties 4-41, the rest require using getters.  
This is to help with performance when polling commonly used variables like voltage/current.  

#### Install
```
git clone https://github.com/ShayBox/Riden.git
cd Riden
python setup.py install --user
```

#### Usage

```py
from riden import Riden
r = Riden("/dev/ttyUSB0")

# Getters
r.get_voltage_set()

# Setters
r.set_voltage_set(3.33)

# Polling (Recommended for accessing many variables)
r.update()
r.voltage_set
r.current_set
```

#### List of Modbus RTU instructions
| Reg ID | Description                             |   |
|--------|-----------------------------------------|---|
| 0      | ID                                      |   |
| 1      | Serial number high bytes                |   |
| 2      | Serial number low bytes                 |   |
| 3      | Firmware version                        |   |
| 4      | Temperature °c sign (0=+, 1=-)          |   |
| 5      | Temperature °c                          |   |
| 6      | Temperature F sign (0=+, 1=-)           |   |
| 7      | Temperature F                           |   |
| 8      | Voltage set value                       |   |
| 9      | Current set value                       |   |
| 10     | Voltage display value                   |   |
| 11     | Current display value                   |   |
| 12     | AH display value                        |   |
| 13     | Power display value                     |   |
| 14     | Voltage input                           |   |
| 15     | Keypad lock                             |   |
| 16     | Protection status (1=OVP, 2=OCP)        |   |
| 17     | CV/CC (0=CV, 1=CC)                      |   |
| 18     | Output enable                           |   |
| 19     | Change preset                           |   |
| 32     | Battery mode active                     |   |
| 33     | Battery voltage                         |   |
| 34     | External temperature °c sign (0=+, 1=-) |   |
| 35     | External temperature °c                 |   |
| 36     | External temperature F sign (0=+, 1=-)  |   |
| 37     | External temperature F                  |   |
| 38     | Ah high bytes                           |   |
| 39     | Ah low bytes                            |   |
| 40     | Wh high bytes                           |   |
| 41     | Wh low bytes                            |   |
| 48     | Year                                    |   |
| 49     | Month                                   |   |
| 50     | Day                                     |   |
| 51     | Hour                                    |   |
| 52     | Minute                                  |   |
| 53     | Second                                  |   |
| 55     | Output Voltage Zero                     |   |
| 56     | Output Voltage Scale                    |   |
| 57     | Back Voltage Zero                       |   |
| 58     | Back Voltage Scale                      |   |
| 59     | Output Current Zero                     |   |
| 60     | Output Current Scale                    |   |
| 61     | Back Current Zero                       |   |
| 62     | Back Current Scale                      |   |
| 66     | Settings Take ok                        |   |
| 67     | Settings Take out                       |   |
| 68     | Settings Boot pow                       |   |
| 69     | Settings Buzzer                         |   |
| 70     | Settings Logo                           |   |
| 71     | Settings Language                       |   |
| 72     | Settings Backlight                      |   |
| 80     | M0 V                                    |   |
| 81     | M0 A                                    |   |
| 82     | M0 OVP                                  |   |
| 83     | M1 OCP                                  |   |
| 84     | M1 V                                    |   |
| 85     | M1 A                                    |   |
| 86     | M1 OVP                                  |   |
| 87     | M1 OCP                                  |   |
| 88     | M2 V                                    |   |
| 89     | M2 A                                    |   |
| 90     | M2 OVP                                  |   |
| 91     | M2 OCP                                  |   |
| 92     | M3 V                                    |   |
| 93     | M3 A                                    |   |
| 94     | M3 OVP                                  |   |
| 95     | M3 OCP                                  |   |
| 96     | M4 V                                    |   |
| 97     | M4 A                                    |   |
| 98     | M4 OVP                                  |   |
| 99     | M4 OCP                                  |   |
| 100    | M5 V                                    |   |
| 101    | M5 A                                    |   |
| 102    | M5 OVP                                  |   |
| 103    | M5 OCP                                  |   |
| 104    | M6 V                                    |   |
| 105    | M6 A                                    |   |
| 106    | M6 OVP                                  |   |
| 107    | M6 OCP                                  |   |
| 108    | M7 V                                    |   |
| 109    | M7 A                                    |   |
| 110    | M7 OVP                                  |   |
| 111    | M7 OCP                                  |   |
| 112    | M8 V                                    |   |
| 113    | M8 A                                    |   |
| 114    | M8 OVP                                  |   |
| 115    | M8 OCP                                  |   |
| 116    | M9 V                                    |   |
| 117    | M9 A                                    |   |
| 118    | M9 OVP                                  |   |
| 119    | M9 OCP                                  |   |