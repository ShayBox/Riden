# Riden

A python library for Riden RD power supplies  
This library is based on [Baldanos/rd6006](https://github.com/Baldanos/rd6006)

#### Custom Firmware
It appears Ruiden has changed something in recent stock firmware versions that may break modbus communication.  
I would recommend using UniSoft's custom firmware which is based on older stock firmware, but adds many, many new features.  

#### Installation
Optional:
- [Firmware] UniSoft's custom firmware

Requirements:
- [Python] 3.7 or later
```
$ pip install --user git+https://github.com/shaybox/riden.git
```

Adding to an existing poetry project:
```
$ poetry add git+https://github.com/shaybox/riden.git
```

#### Usage
There's a script to print out basic information about the power supply:
```
$ riden --port=/dev/ttyUSB0 --baudrate 115200
ID      : 60181
SN      : 00011608
FW      : 136
TYPE    : RD6018
INT_C   : 29
INT_F   : 84
V_SET   : 0.0
I_SET   : 0.0
V_OUT   : 0.0
I_OUT   : 0.0
P_OUT   : 0.0
V_IN    : 68.07
KEYPAD  : False
OVP_OCP : None
CV_CC   : CV
OUTPUT  : False
PRESET  : 0
BAT_MODE: False
V_BAT   : 0.0
EXT_C   : -89
EXT_F   : -128
AH      : 0.0
WH      : 0.0
DATETIME: 2022-02-13 11:26:02
TAKE_OK : True
TAKE_OUT: False
BOOT_POW: False
BUZZ    : False
LOGO    : False
LANG    : 0
LIGHT   : 5
```
```python
from riden import Riden

# These are the default values for port, baudrate, and address
r = Riden(port="/dev/ttyUSB0", baudrate=115200, address=1)

# Getters and Setters are available
print(r.get_v_set())
print(r.get_i_set())
r.set_v_set(4.20)
r.set_i_set(0.50)

# Mass polling is available as well
# This reduces the number of reads to the device
r.update()
print(r.v_set)
print(r.i_set)
```

There's also a `Bootloader` class that can be used to update the firmware.  
This is based on [tjko/riden-flashrool](https://github.com/tjko/riden-flashtool)
```
$ riden --port=/dev/ttyUSB0 --baudrate 115200 --firmware path/to/firmware.bin
```
```python
from riden import Bootloader
# Address is only required to reboot the device into bootloader mode via modbus
# These values are the defaults
Bootloader(port="/dev/ttyUSB0", baudrate=115200, address=1).flash("path/to/firmware.bin")
```

#### [List of Modbus RTU registers](https://github.com/Baldanos/rd6006/blob/master/registers.md)
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
| 256    | SYSTEM                                  |   |

[Python]: https://python.org
[Firmware]: https://drive.google.com/file/d/1FKAXFBIbRVujsal-6V2Ta0ogtcvQAIPd/view
