from datetime import datetime
from modbus_tk.defines import (
    READ_HOLDING_REGISTERS,
    WRITE_SINGLE_REGISTER,
    WRITE_MULTIPLE_REGISTERS,
)
from modbus_tk.exceptions import ModbusInvalidResponseError
from modbus_tk.modbus_rtu import RtuMaster
from riden import registers as R
from serial import Serial


class Riden:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, address=1):
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.serial = Serial(port, baudrate)
        self.master = RtuMaster(self.serial)
        self.master.set_timeout(5)
        self.id = self.read(R.ID)
        self.sn = "%08d" % (self.read(R.SN_HIGH) << 16 | self.read(R.SN_LOW))
        self.fw = self.read(R.FW) / 100

        self.voltage_multiplier = 100
        self.current_multiplier = 100
        self.power_multiplier = 100
        self.input_voltage_multiplier = 100

        if 60180 <= self.id <= 60189:
            self.type = "RD6018"
        elif 60120 <= self.id <= 60129:
            self.type = "RD6012"
        elif 60060 <= self.id <= 60064:
            self.type = "RD6006"
            self.current_multiplier = 1000
        elif self.id == 60065:
            self.type = "RD6006P"
            self.voltage_multiplier = 1000
            self.current_multiplier = 10000
            self.power_multiplier = 1000

    def read(self, register: int) -> int:
        try:
            return self.master.execute(
                self.address, READ_HOLDING_REGISTERS, register, 1
            )[0]
        except ModbusInvalidResponseError:
            return self.read(register)

    def read_multiple(self, register: int, length: int) -> tuple:
        try:
            return self.master.execute(
                self.address, READ_HOLDING_REGISTERS, register, length
            )
        except ModbusInvalidResponseError:
            return self.read_multiple(register, length)

    def write(self, register: int, value: int) -> int:
        try:
            return self.master.execute(
                self.address, WRITE_SINGLE_REGISTER, register, output_value=value
            )[1]
        except ModbusInvalidResponseError:
            return self.write(register, value)

    def write_multiple(self, register: int, values: tuple) -> tuple:
        try:
            return self.master.execute(
                self.address, WRITE_MULTIPLE_REGISTERS, register, output_value=values
            )
        except ModbusInvalidResponseError:
            return self.write_multiple(register, values)

    def update(self):
        data = self.read_multiple(0, 42)
        self.get_int_temp_c(data[R.INT_TEMP_C_S], data[R.INT_TEMP_C])
        self.get_int_temp_f(data[R.INT_TEMP_F_S], data[R.INT_TEMP_F])
        self.get_voltage_set(data[R.V_SET])
        self.get_current_set(data[R.I_SET])
        self.get_voltage(data[R.V_DISPLAY])
        self.get_current(data[R.I_DISPLAY])
        self.get_power(data[R.POWER])
        self.get_voltage_input(data[R.V_INPUT])
        self.is_keypad_lock(data[R.KEYPAD_LOCK])
        self.get_protection(data[R.PROTECTION])
        self.get_protection_string(data[R.PROTECTION])
        self.get_constant(data[R.CONSTANT])
        self.get_constant_string(data[R.CONSTANT])
        self.is_output(data[R.OUTPUT])
        self.get_preset(data[R.PRESET])
        self.get_battery_mode(data[R.BAT_MODE])
        self.get_battery_voltage(data[R.BAT_VOLTAGE])
        self.get_ext_temp_c(data[R.EXT_TEMP_C_S], data[R.EXT_TEMP_C])
        self.get_ext_temp_f(data[R.EXT_TEMP_F_S], data[R.EXT_TEMP_F])
        self.get_amperehour(data[R.AH_HIGH], data[R.AH_LOW])
        self.get_watthour(data[R.WH_HIGH], data[R.WH_LOW])

    def get_int_temp_c(self, sign: int = None, temp: int = None) -> int:
        if sign is None:
            sign = self.read(R.INT_TEMP_C_S)
        if temp is None:
            temp = self.read(R.INT_TEMP_C)

        multiple = -1 if sign else +1
        self.int_temp_c = temp * multiple
        return self.int_temp_c

    def get_int_temp_f(self, sign: int = None, temp: int = None) -> int:
        if sign is None:
            sign = self.read(R.INT_TEMP_F_S)
        if temp is None:
            temp = self.read(R.INT_TEMP_F)

        multiple = -1 if sign else +1
        self.int_temp_f = temp * multiple
        return self.int_temp_f

    def get_voltage_set(self, voltage: int = None) -> float:
        if voltage is None:
            voltage = self.read(R.V_SET)

        self.voltage_set = voltage / self.voltage_multiplier
        return self.voltage_set

    def set_voltage_set(self, value: float) -> float:
        voltage = round(value * self.voltage_multiplier)
        return self.write(R.V_SET, int(voltage))

    def get_current_set(self, current: int = None) -> float:
        if current is None:
            current = self.read(R.I_SET)

        self.current_set = current / self.current_multiplier
        return self.current_set

    def set_current_set(self, value: float) -> float:
        current = round(value * self.current_multiplier)
        return self.write(R.I_SET, int(current))

    def get_voltage(self, voltage: int = None) -> float:
        if voltage is None:
            voltage = self.read(R.V_DISPLAY)

        self.voltage = voltage / self.voltage_multiplier
        return self.voltage

    def get_current(self, current: int = None) -> float:
        if current is None:
            current = self.read(R.I_DISPLAY)

        self.current = current / self.current_multiplier
        return self.current

    def get_power(self, power: int = None) -> float:
        if power is None:
            power = self.read(R.POWER)

        self.power = power / self.power_multiplier
        return self.power

    def get_voltage_input(self, voltage: int = None) -> float:
        if voltage is None:
            voltage = self.read(R.V_INPUT)

        self.voltage_input = voltage / self.input_voltage_multiplier
        return self.voltage_input

    def is_keypad_lock(self, keypad: int = None) -> bool:
        if keypad is None:
            keypad = self.read(R.KEYPAD_LOCK)

        self.keypad_lock = bool(keypad)
        return self.keypad_lock

    def get_protection(self, protection: int = None) -> int:
        if protection is None:
            protection = self.read(R.PROTECTION)

        self.protection = protection
        return self.protection

    def get_protection_string(self, protection: int = None) -> str:
        if protection is None:
            protection = self.get_protection(protection)

        self.protection_string = (
            "OVP" if protection == 1 else "OCP" if protection == 2 else "None"
        )
        return self.protection_string

    def get_constant(self, constant: int = None) -> int:
        if constant is None:
            constant = self.read(R.CONSTANT)

        self.constant = constant
        return self.constant

    def get_constant_string(self, constant: int = None) -> str:
        if constant is None:
            constant = self.get_constant(constant)

        self.constant_string = (
            "CV" if constant == 0 else "CC" if constant == 1 else "None"
        )
        return self.constant_string

    def is_output(self, output: int = None) -> bool:
        if output is None:
            output = self.read(R.OUTPUT)

        self.output = bool(output)
        return self.output

    def set_output(self, state: bool):
        return self.write(R.OUTPUT, int(state))

    def get_preset(self, preset: int = None) -> int:
        if preset is None:
            preset = self.read(R.PRESET)

        self.preset = preset
        return self.preset

    def get_battery_mode(self, battery_mode: int = None) -> int:
        if battery_mode is None:
            battery_mode = self.read(R.BAT_MODE)

        self.battery_mode = battery_mode
        return self.battery_mode

    def get_battery_voltage(self, voltage: int = None) -> float:
        if voltage is None:
            voltage = self.read(R.BAT_VOLTAGE)

        self.battery_voltage = voltage / self.voltage_multiplier
        return self.battery_voltage

    def get_ext_temp_c(self, sign: int = None, temp: int = None) -> int:
        if sign is None:
            sign = self.read(R.EXT_TEMP_C_S)
        if temp is None:
            temp = self.read(R.EXT_TEMP_C)

        multiple = -1 if sign else +1
        self.ext_temp_c = temp * multiple
        return self.ext_temp_c

    def get_ext_temp_f(self, sign: int = None, temp: int = None) -> int:
        if sign is None:
            sign = self.read(R.EXT_TEMP_F_S)
        if temp is None:
            temp = self.read(R.EXT_TEMP_F)

        multiple = -1 if sign else +1
        self.ext_temp_f = temp * multiple
        return self.ext_temp_f

    def get_amperehour(self, high: int = None, low: int = None) -> float:
        if high is None:
            high = self.read(R.AH_HIGH)
        if low is None:
            low = self.read(R.AH_LOW)

        self.amperehour = (high << 16 | low) / 1000
        return self.amperehour

    def get_watthour(self, high: int = None, low: int = None) -> float:
        if high is None:
            high = self.read(R.AH_HIGH)
        if low is None:
            low = self.read(R.AH_LOW)

        self.watthour = (high << 16 | low) / 1000
        return self.watthour

    def get_date_time(self) -> datetime:
        d = self.read_multiple(48, 6)
        self.datetime = datetime(d[0], d[1], d[2], d[3], d[4], d[5])
        return self.datetime

    def set_date_time(self, d: datetime) -> int:
        return self.write_multiple(
            48, (d.year, d.month, d.day, d.hour, d.minute, d.second)
        )

    def is_confirm(self) -> bool:
        confirm = self.read(R.S_CONFIRM)
        self.confirm = bool(confirm)
        return self.confirm

    def set_confirm(self, value: bool) -> int:
        return self.write(R.S_CONFIRM, int(value))

    def is_restore(self) -> bool:
        restore = self.read(R.S_RESTORE)
        self.restore = bool(restore)
        return self.restore

    def set_restore(self, value: bool) -> int:
        return self.write(R.S_RESTORE, int(value))

    def is_boot_power(self) -> bool:
        boot_power = self.read(R.S_BOOT_POWER)
        self.boot_power = bool(boot_power)
        return self.boot_power

    def set_boot_power(self, value: bool) -> int:
        return self.write(R.S_BOOT_POWER, int(value))

    def is_buzzer(self) -> bool:
        buzzer = self.read(R.S_BUZZER)
        self.buzzer = bool(buzzer)
        return self.buzzer

    def set_buzzer(self, value: bool) -> int:
        return self.write(R.S_BUZZER, int(value))

    def is_boot_logo(self) -> bool:
        boot_logo = self.read(R.S_BOOT_LOGO)
        self.boot_logo = bool(boot_logo)
        return self.boot_logo

    def set_boot_logo(self, value: bool) -> int:
        return self.write(R.S_BOOT_LOGO, int(value))

    def get_language(self) -> bool:
        self.language = self.read(R.S_LANGUAGE)
        return self.language

    def set_language(self, value: bool) -> int:
        return self.write(R.S_LANGUAGE, int(value))

    def get_backlight(self) -> bool:
        self.backlight = self.read(R.S_BACKLIGHT)
        return self.backlight

    def set_backlight(self, value: bool) -> int:
        return self.write(R.S_BACKLIGHT, int(value))


def main():
    r = Riden()
    r.update()
    data = {
        "ID         :": r.id,
        "SN         :": r.sn,
        "FW         :": r.fw,
        "Type       :": r.type,
        "Int Temp C :": r.int_temp_c,
        "Int Temp F :": r.int_temp_f,
        "V-Set      :": r.voltage_set,
        "I-Set      :": r.current_set,
        "Voltage    :": r.voltage,
        "Current    :": r.current,
        "Power      :": r.power,
        "V-Input    :": r.voltage_input,
        "Keypad     :": r.keypad_lock,
        "Protection :": r.protection_string,
        "Constant   :": r.constant_string,
        "Output     :": r.output,
        "Preset     :": r.preset,
        "Bat-Mode   :": r.battery_mode,
        "Bat-Voltage:": r.battery_voltage,
        "Ext Temp C :": r.ext_temp_c,
        "Ext Temp F :": r.ext_temp_f,
        "AmpereHour :": r.amperehour,
        "WattHour   :": r.watthour,
        "DateTime   :": r.get_date_time(),
        "Confirm    :": r.is_confirm(),
        "Restore    :": r.is_restore(),
        "Boot Power :": r.is_boot_power(),
        "Buzzer     :": r.is_buzzer(),
        "Boot Logo  :": r.is_boot_logo(),
        "Language   :": r.get_language(),
        "Backlight  :": r.get_backlight(),
    }
    for key, value in data.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
