# Built-in modules
from time import sleep

# Third-party modules
from serial import Serial

# Local modules
from riden.riden import Riden


class Bootloader:
    def __init__(
        self, port: str, baudrate: int, address: int, verbose: bool = False
    ):
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.verbose = verbose

        self.init()
        self.info()

    def init(self) -> None:
        print("Checking if the device is in bootloaer mode...")
        if not self.check_bootloader():
            print("Device is not in bootloader mode")
            r = Riden(address=self.address, serial=self.serial)
            print(f"Found device: {r.type}")
            print("Attempting to enter bootloader mode...")
            r.reboot_bootloader()
            sleep(5)  # Wait for device to reboot
            if not self.check_bootloader():
                raise Exception("Failed to enter bootloader mode")

    def info(self):
        self.write(b"getinf\r\n")
        res = self.read(13)

        if len(res) == 0:
            raise Exception("No response from device.")
        if len(res) != 13 or res[0:3] != b"inf":
            raise Exception("Invalid response received.")

        print(f"Device found: RD{(res[8] << 8 | res[7]) / 10:.0f}")

    def check_bootloader(self) -> bool:
        print(f"Opening {self.port} at {self.baudrate} baud")
        self.serial = Serial(self.port, self.baudrate, timeout=5)

        self.write(b"queryd\r\n")
        return self.read(4) == b"boot"

    def read(self, size: int):
        res = self.serial.read(size)
        if self.verbose:
            print(f"Read | Len: {len(res)} | Res: {res} | Size: {size}")
        return res

    def write(self, data):
        res = self.serial.write(data)
        if self.verbose:
            print(f"Write| Len: {len(data)} | Data: {data} | Res: {res}")
        return res

    def flash(self, file):
        print("Attempting to enter flash mode...")
        self.write(b"upfirm\r\n")
        if self.read(6) != b"upredy":
            raise Exception("Failed to enter flash mode.")

        print("Flashing firmware...")
        firmware = file.read()
        file.close()

        pos, size = 0, 64
        while pos < len(firmware):
            buf = firmware[pos : pos + size]
            self.write(buf)
            res = self.read(2)
            if res != b"OK":
                raise Exception(f"Failed to flash firmware: {res}")
            if not self.verbose:
                print(".", end="", flush=True)
            pos += size
