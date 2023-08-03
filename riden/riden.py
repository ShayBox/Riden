# Built-in modules
from datetime import datetime
from typing import Optional

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


Number = int | float

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

        if 60241 <= self.id:  # type: ignore
            self.type = "RD6024"
        elif 60180 <= self.id <= 60189:  # type: ignore
            self.type = "RD6018"
        elif 60120 <= self.id <= 60124:  # type: ignore
            self.type = "RD6012"
        elif 60125 <= self.id <= 60129:  # type: ignore
            self.type = "RD6012P"
            self.v_multi = 1000
            self.p_multi = 1000
            # i_multi is not constant!
        elif 60060 <= self.id <= 60064:  # type: ignore
            self.type = "RD6006"
            self.i_multi = 1000
        elif self.id == 60065:
            self.type = "RD6006P"
            self.v_multi = 1000
            self.i_multi = 10000
            self.p_multi = 1000

        self.update()

    def read(self, register: int, length: int = 1) -> int | tuple:
        try:
            response = self.master.execute(
                self.address, READ_HOLDING_REGISTERS, register, length
            )
            return response if length > 1 else response[0]
        except ModbusInvalidResponseError:
            return self.read(register, length)


    def write(self, register: int, value: int) -> int:
        try:
            return self.master.execute(
                self.address, WRITE_SINGLE_REGISTER, register, 1, value
            )[0]
        except ModbusInvalidResponseError:
            return self.write(register, value)

    def write_multiple(self, register: int, values: list | tuple) -> tuple:
        try:
            return self.master.execute(
                self.address, WRITE_MULTIPLE_REGISTERS, register, 1, values  # type: ignore
            )
        except ModbusInvalidResponseError:
            return self.write_multiple(register, values)

    def init(self) -> None:
        data = self.read(R.ID, R.FW + 1)
        assert isinstance(data, tuple), "unexpected modbus response or type conflict"
        self.get_id(data[R.ID])
        self.get_sn(data[R.SN_H], data[R.SN_L])
        self.get_fw(data[R.FW])

    def get_id(self, _id: Optional[int] = None) -> int:
        self.id = self.read(R.ID) if _id is None else _id
        assert isinstance(self.id, int), "unexpected modbus response or type conflict"
        return self.id

    def get_sn(self,
               _sn_h: Optional[int] = None,
               _sn_l: Optional[int] = None) -> str:
        sn_h = self.read(R.SN_H) if _sn_h is None else _sn_h
        sn_l = self.read(R.SN_L) if _sn_l is None else _sn_l
        assert isinstance(sn_h, int), "unexpected modbus response or type conflict"
        assert isinstance(sn_l, int), "unexpected modbus response or type conflict"
        self.sn = "%08d" % (sn_h << 16 | sn_l)
        return self.sn

    def get_fw(self, _fw: Optional[int] = None) -> int:
        self.fw = self.read(R.FW) if _fw is None else _fw
        assert isinstance(self.fw, int), "unexpected modbus response or type conflict"
        return self.fw

    def update(self) -> None:
        data = (None,) * 4  # Fix offset - Init registers
        data_read = self.read(R.INT_C_S, (R.I_RANGE - R.INT_C_S) + 1)
        assert isinstance(data_read, tuple), "unexpected modbus response or type conflict"
        data += data_read
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
        data_read = self.read(R.BAT_MODE, (R.WH_L - R.BAT_MODE) + 1)
        assert isinstance(data_read, tuple), "unexpected modbus response or type conflict"
        data += data_read
        self.is_bat_mode(data[R.BAT_MODE])
        self.get_v_bat(data[R.V_BAT])
        self.get_ext_c(data[R.EXT_C_S], data[R.EXT_C])
        self.get_ext_f(data[R.EXT_F_S], data[R.EXT_F])
        self.get_ah(data[R.AH_H], data[R.AH_L])
        self.get_wh(data[R.WH_H], data[R.WH_L])

    def get_int_c(self,
                  _int_c_s: Optional[int] = None,
                  _int_c: Optional[int] = None) -> int:
        int_c_s = self.read(R.INT_C_S) if _int_c_s is None else _int_c_s
        int_c = self.read(R.INT_C) if _int_c is None else _int_c
        sign = -1 if int_c_s else +1
        assert isinstance(int_c, int), "unexpected modbus response or type conflict"
        self.int_c = int_c * sign
        return self.int_c

    def get_int_f(self,
                  _int_f_s: Optional[int] = None,
                  _int_f: Optional[int] = None) -> int:
        int_f_s = self.read(R.INT_F_S) if _int_f_s is None else _int_f_s
        int_f = self.read(R.INT_F) if _int_f is None else _int_f
        assert isinstance(int_f_s, int), "unexpected modbus response or type conflict"
        assert isinstance(int_f, int), "unexpected modbus response or type conflict"
        sign = -1 if int_f_s else +1
        self.int_f = int_f * sign
        return self.int_f

    def get_v_set(self, _v_set: Optional[Number] = None) -> float:
        v_set = self.read(R.V_SET) if _v_set is None else _v_set
        assert isinstance(v_set, Number), "unexpected modbus response or type conflict"
        self.v_set = v_set / self.v_multi
        return self.v_set

    def set_v_set(self, v_set: Number) -> float:
        self.v_set = round(v_set * self.v_multi)
        return self.write(R.V_SET, int(self.v_set))

    def get_i_set(self, _i_set: Optional[Number] = None) -> float:
        i_set = self.read(R.I_SET) if _i_set is None else _i_set
        assert isinstance(i_set, Number), "unexpected modbus response or type conflict"
        self.i_set = i_set / self.i_multi
        return self.i_set

    def set_i_set(self, i_set: Number) -> int:
        self.i_set = round(i_set * self.i_multi)
        return self.write(R.I_SET, int(self.i_set))

    def get_v_out(self, _v_out: Optional[Number] = None) -> float:
        v_out = self.read(R.V_OUT) if _v_out is None else _v_out
        assert isinstance(v_out, Number), "unexpected modbus response or type conflict"
        self.v_out = v_out / self.v_multi
        return self.v_out

    def get_i_out(self, _i_out: Optional[Number] = None) -> float:
        i_out = self.read(R.I_OUT) if _i_out is not None else _i_out
        assert isinstance(i_out, Number), "unexpected modbus response or type conflict"
        self.i_out = i_out / self.i_multi
        return self.i_out

    def get_p_out(self, _p_out: Optional[Number] = None) -> float:
        p_out = self.read(R.P_OUT) if _p_out is None else _p_out
        assert isinstance(p_out, Number), "unexpected modbus response or type conflict"
        self.p_out = p_out / self.p_multi
        return self.p_out

    def get_v_in(self, _v_in: Optional[Number] = None) -> float:
        v_in = self.read(R.V_IN) if _v_in else _v_in
        assert isinstance(v_in, Number), "unexpected modbus response or type conflict"
        self.v_in = v_in / self.v_in_multi
        return self.v_in

    def is_keypad(self, _keypad: Optional[int] = None) -> bool:
        self.keypad = bool(_keypad or self.read(R.KEYPAD))
        return self.keypad

    def get_ovp_ocp(self, _ovp_ocp: Optional[int] = None) -> Optional[str]:
        ovp_ocp = self.read(R.OVP_OCP) if _ovp_ocp is None else _ovp_ocp
        assert isinstance(ovp_ocp, int), "unexpected modbus response or type conflict"
        self.ovp_ocp = (
            "OVP" if ovp_ocp == 1 else "OCP" if ovp_ocp == 2 else None
        )
        return self.ovp_ocp

    def get_cv_cc(self, _cv_cc: Optional[int] = None) -> Optional[str]:
        cv_cc = self.read(R.CV_CC) if _cv_cc is None else _cv_cc
        assert isinstance(cv_cc, int), "unexpected modbus response or type conflict"
        self.cv_cc = "CV" if cv_cc == 0 else "CC" if cv_cc == 1 else None
        return self.cv_cc

    def is_output(self, _output: Optional[int] = None) -> bool:
        self.output = bool(_output or self.read(R.OUTPUT))
        return self.output

    def set_output(self, output: bool) -> None:
        self.output = output
        self.write(R.OUTPUT, int(self.output))

    def get_preset(self, _preset: Optional[int] = None) -> int:
        "Always returns 0 on my device, setter works as expected"
        self.preset = self.read(R.PRESET) if _preset is None else _preset
        assert isinstance(self.preset, int), "unexpected modbus response or type conflict"
        return self.preset

    def set_preset(self, preset: int) -> int:
        self.preset = preset
        return self.write(R.PRESET, self.preset)

    def is_bat_mode(self, _bat_mode: Optional[bool] = None) -> bool:
        self.bat_mode = bool(self.read(R.BAT_MODE)) if _bat_mode is None else _bat_mode
        return self.bat_mode

    def get_v_bat(self, _v_bat: Optional[Number] = None) -> float:
        v_bat = self.read(R.V_BAT) if _v_bat is None else _v_bat
        assert isinstance(v_bat, Number), "unexpected modbus response or type conflict"
        self.v_bat = v_bat / self.v_multi
        return self.v_bat

    def get_ext_c(self,
                  _ext_c_s: Optional[int] = None,
                  _ext_c: Optional[int] = None) -> int:
        ext_c_s = self.read(R.EXT_C_S) if _ext_c_s else _ext_c_s
        ext_c =  self.read(R.EXT_C) if _ext_c else _ext_c
        sign = -1 if ext_c_s else +1
        assert isinstance(ext_c, int), "unexpected modbus response or type conflict"
        self.ext_c = ext_c * sign
        return self.ext_c

    def get_ext_f(self,
                  _ext_f_s: Optional[int] = None,
                  _ext_f: Optional[int] = None) -> int:
        ext_f_s = self.read(R.EXT_F_S) if _ext_f_s else _ext_f_s
        ext_f =  self.read(R.EXT_F) if _ext_f else _ext_f
        sign = -1 if ext_f_s else +1
        assert isinstance(ext_f, int), "unexpected modbus response or type conflict"
        self.ext_f = ext_f * sign
        assert isinstance(self.ext_f, int), "unexpected modbus response or type conflict"
        return self.ext_f

    def get_ah(self,
               _ah_h: Optional[int] = None,
               _ah_l: Optional[int] = None) -> float:
        ah_h = self.read(R.AH_H) if _ah_h else _ah_h
        ah_l = self.read(R.AH_L) if _ah_l else _ah_l
        assert isinstance(ah_h, int), "unexpected modbus response or type conflict"
        assert isinstance(ah_l, int), "unexpected modbus response or type conflict"
        self.ah = (ah_h << 16 | ah_l) / 1000
        return self.ah

    def get_wh(self,
               _wh_h: Optional[int] = None,
               _wh_l: Optional[int] = None) -> float:
        wh_h = self.read(R.WH_H) if _wh_h else _wh_h
        wh_l = self.read(R.WH_L) if _wh_l else _wh_l
        assert isinstance(wh_h, int), "unexpected modbus response or type conflict"
        assert isinstance(wh_l, int), "unexpected modbus response or type conflict"
        self.wh = (wh_h << 16 | wh_l) / 1000
        return self.wh

    def get_date_time(self) -> datetime:
        d = self.read(R.YEAR, 6)
        assert isinstance(d, tuple), "unexpected modbus response or type conflict"
        self.datetime = datetime(d[0], d[1], d[2], d[3], d[4], d[5])
        return self.datetime

    def set_date_time(self, d: datetime) -> tuple:
        return self.write_multiple(
            R.YEAR, (d.year, d.month, d.day, d.hour, d.minute, d.second)
        )

    def is_take_ok(self, _take_ok: Optional[int] = None) -> bool:
        self.take_ok = bool(self.read(R.OPT_TAKE_OK) if _take_ok is None else _take_ok)
        return self.take_ok

    def set_take_ok(self, take_ok: bool) -> int:
        self.take_ok = take_ok
        return self.write(R.OPT_TAKE_OK, self.take_ok)

    def is_take_out(self, _take_out: Optional[bool] = None) -> bool:
        self.take_out = bool(self.read(R.OPT_TAKE_OUT) if _take_out is None else _take_out)
        return self.take_out

    def set_take_out(self, take_out: bool) -> bool:
        self.take_out = take_out
        return bool(self.write(R.OPT_TAKE_OUT, self.take_out))

    def is_boot_pow(self, _boot_pow: Optional[bool] = None) -> bool:
        self.boot_pow = bool(self.read(R.OPT_BOOT_POW) if _boot_pow is None else _boot_pow)
        return self.boot_pow

    def set_boot_pow(self, boot_pow: bool) -> bool:
        self.boot_pow = boot_pow
        return bool(self.write(R.OPT_BOOT_POW, self.boot_pow))

    def is_buzz(self, _buzz: Optional[bool] = None) -> bool:
        self.buzz = bool(self.read(R.OPT_BUZZ) if _buzz is None else _buzz)
        return self.buzz

    def set_buzz(self, buzz: bool) -> bool:
        self.buzz = buzz
        return bool(self.write(R.OPT_BUZZ, self.buzz))

    def is_logo(self, _logo: Optional[int] = None) -> bool:
        self.logo = bool(self.read(R.OPT_LOGO) if _logo is None else _logo)
        return self.logo

    def set_logo(self, logo: bool) -> bool:
        self.logo = logo
        return bool(self.write(R.OPT_LOGO, self.logo))

    def get_lang(self) -> int:
        self.lang = self.read(R.OPT_LANG)
        assert isinstance(self.lang, int), "unexpected modbus response or type conflict"
        return self.lang

    def set_lang(self, lang: int) -> int:
        self.lang = lang
        return self.write(R.OPT_LANG, self.lang)

    def get_light(self) -> int:
        self.light = self.read(R.OPT_LIGHT)
        assert isinstance(self.light, int), "unexpected modbus response or type conflict"
        return self.light

    def set_light(self, light: int) -> int:
        self.light = light
        return self.write(R.OPT_LIGHT, self.light)

    def reboot_bootloader(self) -> None:
        try:
            self.write(R.SYSTEM, R.BOOTLOADER)
        except ModbusInvalidResponseError:
            pass
