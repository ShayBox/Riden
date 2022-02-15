# Third-party modules
import click

# Local modules
from .bootloader import Bootloader
from .riden import Riden


@click.command()
@click.option("-p", "--port", default="/dev/ttyUSB0", help="Serial port")
@click.option("-b", "--baudrate", default=115200, help="Serial baudrate")
@click.option("-a", "--address", default=1, help="Modbus address")
@click.option("-f", "--firmware", type=click.File("rb"), help="Firmware file")
def main(port: str, baudrate: int, address: int, firmware):
    if firmware:
        Bootloader(port, baudrate, address).flash(firmware)
    else:
        r = Riden(port, baudrate, address)
        lines = {
            "ID      ": r.id,
            "SN      ": r.sn,
            "FW      ": r.fw,
            "TYPE    ": r.type,
            "INT_C   ": r.int_c,
            "INT_F   ": r.int_f,
            "V_SET   ": r.v_set,
            "I_SET   ": r.i_set,
            "V_OUT   ": r.v_out,
            "I_OUT   ": r.i_out,
            "P_OUT   ": r.p_out,
            "V_IN    ": r.v_in,
            "KEYPAD  ": r.keypad,
            "OVP_OCP ": r.ovp_ocp,
            "CV_CC   ": r.cv_cc,
            "OUTPUT  ": r.output,
            "PRESET  ": r.preset,
            "BAT_MODE": r.bat_mode,
            "V_BAT   ": r.v_bat,
            "EXT_C   ": r.ext_c,
            "EXT_F   ": r.ext_f,
            "AH      ": r.ah,
            "WH      ": r.wh,
            "DATETIME": r.get_date_time(),
            "TAKE_OK ": r.is_take_ok(),
            "TAKE_OUT": r.is_take_out(),
            "BOOT_POW": r.is_boot_pow(),
            "BUZZ    ": r.is_buzz(),
            "LOGO    ": r.is_logo(),
            "LANG    ": r.get_lang(),
            "LIGHT   ": r.get_light(),
        }
        for key, value in lines.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
