# Built-in modules
from datetime import datetime
from typing import Optional, Union

# Third-party modules
from modbus_tk import hooks
from modbus_tk.defines import (
    READ_HOLDING_REGISTERS,
    WRITE_MULTIPLE_REGISTERS,
    WRITE_SINGLE_REGISTER,
)
from modbus_tk.exceptions import ModbusInvalidResponseError
from modbus_tk.modbus_rtu import RtuMaster
from serial import Serial

# Local modules
from .register import Register as R


class Riden:
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 115200,
        address: int = 1,
        serial: Optional[Serial] = None,
        master: Optional[RtuMaster] = None,
        close_after_call: bool = False,
        timeout: float = 0.5,
    ):
        self.address = address
        self.serial = serial or Serial(port, baudrate)
        self.master = master or RtuMaster(self.serial)

        # Fixes "Response length is invalid 0" error
        # If you experience this error, try changing your baudrate
        self.master.set_timeout(timeout)

        # Windows requires opening/closing the com port after each call
        # This is a workaround that will drasticly reduce performance
        if close_after_call:
            hooks.install_hook(
                "modbus_rtu.RtuMaster.before_send", lambda self: self._do_open()
            )
            hooks.install_hook(
                "modbus_rtu.RtuMaster.after_recv", lambda self: self._do_close()
            )

        self.init()

        self.v_multi = 100
        self.i_multi = 100
        self.p_multi = 100
        self.v_in_multi = 100

        if 60241 <= self.id:
            self.type = "RD6024"
        elif 60180 <= self.id <= 60189:
            self.type = "RD6018"
        elif 60120 <= self.id <= 60124:
            self.type = "RD6012"
        elif 60125 <= self.id <= 60129:
            self.type = "RD6012P"
            self.v_multi = 1000
            self.p_multi = 1000
            # i_multi is not constant!
        elif 60060 <= self.id <= 60064:
            self.type = "RD6006"
            self.i_multi = 1000
        elif self.id == 60065:
            self.type = "RD6006P"
            self.v_multi = 1000
            self.i_multi = 10000
            self.p_multi = 1000

        self.update()

    def read(self, register: int, length) -> tuple:
        try:
            response = self.master.execute(
                self.address, READ_HOLDING_REGISTERS, register, length
            )
            return response
        except ModbusInvalidResponseError:
            return self.read(register, length)

    def read_single(self, register: int) -> int:
        response = self.read(register, 1)
        response_len = len(response)
        if response_len > 1:
            raise ValueError(f'unexpected response of length {response_len}')
        return response[0]

    def write_single(self, register: int, value: int) -> int:
        try:
            return self.master.execute(
                self.address, WRITE_SINGLE_REGISTER, register, 1, value
            )[0]
        except ModbusInvalidResponseError:
            return self.write_single(register, value)

    def write_multiple(self, register: int, values: Union[list,
                                                          tuple]) -> tuple:
        try:
            return self.master.execute(
                self.address, WRITE_MULTIPLE_REGISTERS, register, 1, values  # type: ignore
            )
        except ModbusInvalidResponseError:
            return self.write_multiple(register, values)

    def init(self) -> None:
        data = self.read(R.ID, R.FW + 1)
        self.get_id(data[R.ID]),  # type: ignore
        self.get_sn(data[R.SN_H], data[R.SN_L]),  # type: ignore
        self.get_fw(data[R.FW]),  # type: ignore

    def get_id(self, _id: Optional[int] = None) -> Optional[int]:
        self.id = _id or self.read_single(R.ID)
        return self.id

    def get_sn(self,
               _sn_h: Optional[int] = None,
               _sn_l: Optional[int] = None) -> str:
        _sn_h = _sn_h or self.read_single(R.SN_H)
        _sn_l = _sn_l or self.read_single(R.SN_L)
        self.sn = "%08d" % (_sn_h << 16 | _sn_l)
        return self.sn

    def get_fw(self, _fw: Optional[int] = None) -> int:
        self.fw = _fw or self.read_single(R.FW)
        return self.fw

    def update(self) -> None:
        data = (None,) * 4  # Fix offset - Init registers
        data += self.read(R.INT_C_S, (R.I_RANGE - R.INT_C_S) + 1)
        if self.type == "RD6012P":
            if data[R.I_RANGE] == 0:
                self.i_multi = 10000
            else:
                self.i_multi = 1000
        self.get_int_c(data[R.INT_C_S], data[R.INT_C])
        self.get_int_f(data[R.INT_F_S], data[R.INT_F])
        self.get_v_set(data[R.V_SET])
        self.get_i_set(data[R.I_SET])
        self.get_v_out(data[R.V_OUT])
        self.get_i_out(data[R.I_OUT])
        self.get_p_out(data[R.P_OUT])
        self.get_v_in(data[R.V_IN])
        self.is_keypad(data[R.KEYPAD])
        self.get_ovp_ocp(data[R.OVP_OCP])
        self.get_cv_cc(data[R.CV_CC])
        self.is_output(data[R.OUTPUT])
        self.get_preset(data[R.PRESET])
        data += (None,) * 11  # Fix offset - Unused/Unknown registers
        data += self.read(R.BAT_MODE, (R.WH_L - R.BAT_MODE) + 1)
        self.is_bat_mode(data[R.BAT_MODE])
        self.get_v_bat(data[R.V_BAT])
        self.get_ext_c(data[R.EXT_C_S], data[R.EXT_C])
        self.get_ext_f(data[R.EXT_F_S], data[R.EXT_F])
        self.get_ah(data[R.AH_H], data[R.AH_L])
        self.get_wh(data[R.WH_H], data[R.WH_L])

    def get_int_c(self,
                  _int_c_s: Optional[int] = None,
                  _int_c: Optional[int] = None) -> int:
        _int_c_s = _int_c_s or self.read_single(R.INT_C_S)
        _int_c = _int_c or self.read_single(R.INT_C)
        sign = -1 if _int_c_s else +1
        self.int_c = _int_c * sign
        return self.int_c

    def get_int_f(self,
                  _int_f_s: Optional[int] = None,
                  _int_f: Optional[int] = None) -> int:
        _int_f_s = _int_f_s or self.read_single(R.INT_F_S)
        _int_f = _int_f or self.read_single(R.INT_F)
        sign = -1 if _int_f_s else +1
        self.int_f = _int_f * sign
        return self.int_f

    def get_v_set(self, _v_set: Optional[int] = None) -> float:
        _v_set = _v_set or self.read_single(R.V_SET)
        self.v_set = _v_set / self.v_multi
        return self.v_set

    def set_v_set(self, v_set: float) -> float:
        self.v_set = round(v_set * self.v_multi)
        return self.write_single(R.V_SET, int(self.v_set))

    def get_i_set(self, _i_set: Optional[int] = None) -> float:
        _i_set = _i_set or self.read_single(R.I_SET)
        self.i_set = _i_set / self.i_multi
        return self.i_set

    def set_i_set(self, i_set: float) -> float:
        self.i_set = round(i_set * self.i_multi)
        return self.write_single(R.I_SET, int(self.i_set))

    def get_v_out(self, _v_out: Optional[int] = None) -> float:
        _v_out = _v_out or self.read_single(R.V_OUT)
        self.v_out = _v_out / self.v_multi
        return self.v_out

    def get_i_out(self, _i_out: Optional[int] = None) -> float:
        _i_out = _i_out or self.read_single(R.I_OUT)
        self.i_out = _i_out / self.i_multi
        return self.i_out

    def get_p_out(self, _p_out: Optional[int] = None) -> float:
        _p_out = _p_out or self.read_single(R.P_OUT)
        self.p_out = _p_out / self.p_multi
        return self.p_out

    def get_v_in(self, _v_in: Optional[int] = None) -> float:
        _v_in = _v_in or self.read_single(R.V_IN)
        self.v_in = _v_in / self.v_in_multi
        return self.v_in

    def is_keypad(self, _keypad: Optional[int] = None) -> bool:
        self.keypad = bool(_keypad or self.read_single(R.KEYPAD))
        return self.keypad

        _ovp_ocp = _ovp_ocp or self.read(R.OVP_OCP)
        self.ovp_ocp = (
            "OVP" if _ovp_ocp == 1 else "OCP" if _ovp_ocp == 2 else None
        )
    def get_ovp_ocp(self, _ovp_ocp: Optional[int] = None) -> Optional[str]:
        return self.ovp_ocp

    def get_cv_cc(self, _cv_cc: Optional[int] = None) -> Optional[str]:
        _cv_cc = _cv_cc or self.read_single(R.CV_CC)
        self.cv_cc = "CV" if _cv_cc == 0 else "CC" if _cv_cc == 1 else None
        return self.cv_cc

    def is_output(self, _output: Optional[int] = None) -> bool:
        self.output = bool(_output or self.read_single(R.OUTPUT))
        return self.output

    def set_output(self, output: bool) -> None:
        self.output = output
        self.write_single(R.OUTPUT, int(self.output))

    def get_preset(self, _preset: Optional[int] = None) -> int:
        "Always returns 0 on my device, setter works as expected"
        self.preset = _preset or self.read_single(R.PRESET)
        return self.preset

    def set_preset(self, preset: int) -> int:
        self.preset = preset
        return self.write_single(R.PRESET, self.preset)

    def is_bat_mode(self, _bat_mode: Optional[int] = None) -> bool:
        self.bat_mode = bool(_bat_mode or self.read_single(R.BAT_MODE))
        return self.bat_mode

    def get_v_bat(self, _v_bat: Optional[int] = None) -> float:
        _v_bat = _v_bat or self.read_single(R.V_BAT)
        self.v_bat = _v_bat / self.v_multi
        return self.v_bat

    def get_ext_c(self,
                  _ext_c_s: Optional[int] = None,
                  _ext_c: Optional[int] = None) -> int:
        _ext_c_s = _ext_c_s or self.read_single(R.EXT_C_S)
        _ext_c = _ext_c or self.read_single(R.EXT_C)
        sign = -1 if _ext_c_s else +1
        self.ext_c = _ext_c * sign
        return self.ext_c

    def get_ext_f(self,
                  _ext_f_s: Optional[int] = None,
                  _ext_f: Optional[int] = None) -> int:
        _ext_f_s = _ext_f_s or self.read_single(R.EXT_F_S)
        _ext_f = _ext_f or self.read_single(R.EXT_F)
        sign = -1 if _ext_f_s else +1
        self.ext_f = _ext_f * sign
        return self.ext_f

    def get_ah(self,
               _ah_h: Optional[int] = None,
               _ah_l: Optional[int] = None) -> float:
        _ah_h = _ah_h or self.read_single(R.AH_H)
        _ah_l = _ah_l or self.read_single(R.AH_L)
        self.ah = (_ah_h << 16 | _ah_l) / 1000
        return self.ah

    def get_wh(self,
               _wh_h: Optional[int] = None,
               _wh_l: Optional[int] = None) -> float:
        _wh_h = _wh_h or self.read_single(R.WH_H)
        _wh_l = _wh_l or self.read_single(R.WH_L)
        self.wh = (_wh_h << 16 | _wh_l) / 1000
        return self.wh

    def get_date_time(self) -> datetime:
        d = self.read(R.YEAR, 6)
        self.datetime = datetime(d[0], d[1], d[2], d[3], d[4], d[5])
        return self.datetime

    def set_date_time(self, d: datetime) -> tuple:
        return self.write_multiple(
            R.YEAR, (d.year, d.month, d.day, d.hour, d.minute, d.second)
        )

    def is_take_ok(self, _take_ok: Optional[int] = None) -> bool:
        self.take_ok = bool(_take_ok or self.read_single(R.OPT_TAKE_OK))
        return self.take_ok

    def set_take_ok(self, take_ok: bool) -> int:
        self.take_ok = take_ok
        return self.write_single(R.OPT_TAKE_OK, self.take_ok)

    def is_take_out(self, _take_out: Optional[int] = None) -> bool:
        self.take_out = bool(_take_out or self.read_single(R.OPT_TAKE_OUT))
        return self.take_out

    def set_take_out(self, take_out: bool) -> int:
        self.take_out = take_out
        return self.write_single(R.OPT_TAKE_OUT, self.take_out)

    def is_boot_pow(self, _boot_pow: Optional[int] = None) -> bool:
        self.boot_pow = bool(_boot_pow or self.read_single(R.OPT_BOOT_POW))
        return self.boot_pow

    def set_boot_pow(self, boot_pow: bool) -> int:
        self.boot_pow = boot_pow
        return self.write_single(R.OPT_BOOT_POW, self.boot_pow)

    def is_buzz(self, _buzz: Optional[int] = None) -> int:
        self.buzz = bool(_buzz or self.read_single(R.OPT_BUZZ))
        return self.buzz

    def set_buzz(self, buzz: bool) -> int:
        self.buzz = buzz
        return self.write_single(R.OPT_BUZZ, self.buzz)

    def is_logo(self, _logo: Optional[int] = None) -> bool:
        self.logo = bool(_logo or self.read_single(R.OPT_LOGO))
        return self.logo

    def set_logo(self, logo: bool) -> int:
        self.logo = logo
        return self.write_single(R.OPT_LOGO, self.logo)

    def get_lang(self) -> int:
        self.lang = self.read_single(R.OPT_LANG)
        return self.lang

    def set_lang(self, lang: int) -> int:
        self.lang = lang
        return self.write_single(R.OPT_LANG, self.lang)

    def get_light(self) -> int:
        self.light = self.read_single(R.OPT_LIGHT)
        return self.light

    def set_light(self, light: int) -> int:
        self.light = light
        return self.write_single(R.OPT_LIGHT, self.light)

    def reboot_bootloader(self) -> None:
        try:
            self.write_single(R.SYSTEM, R.BOOTLOADER)
        except ModbusInvalidResponseError:
            pass
