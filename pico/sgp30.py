from machine import I2C, Pin
import time
from math import exp

_SGP30_DEFAULT_I2C_ADDR = 0x58
_SGP30_FEATURESETS = (0x0020, 0x0022)

_SGP30_CRC8_POLYNOMIAL = 0x31
_SGP30_CRC8_INIT = 0xFF
_SGP30_WORD_LEN = 2

class SGP30:
    def __init__(self, i2c: I2C, address: int = _SGP30_DEFAULT_I2C_ADDR) -> None:
        self._i2c = i2c
        self._address = address

        # Get unique serial number (48 bits)
        self.serial = self._i2c_read_words_from_cmd([0x36, 0x82], 0.01, 3)
        # Get feature set
        featureset = self._i2c_read_words_from_cmd([0x20, 0x2F], 0.01, 1)
        if featureset[0] not in _SGP30_FEATURESETS:
            raise RuntimeError("SGP30 Not detected")
        self.iaq_init()

    @property
    def TVOC(self) -> int:
        return self.iaq_measure()[1]

    @property
    def eCO2(self) -> int:
        return self.iaq_measure()[0]

    def iaq_init(self) -> None:
        self._run_profile(("iaq_init", [0x20, 0x03], 0, 0.01))

    def iaq_measure(self) -> list:
        return self._run_profile(("iaq_measure", [0x20, 0x08], 2, 0.05))

    def _run_profile(self, profile: tuple) -> list:
        _, command, signals, delay = profile
        return self._i2c_read_words_from_cmd(command, delay, signals)

    def _i2c_read_words_from_cmd(self, command: list, delay: float, reply_size: int) -> list:
        self._i2c.writeto(self._address, bytes(command))
        time.sleep(delay)
        if not reply_size:
            return []
        crc_result = bytearray(reply_size * (_SGP30_WORD_LEN + 1))
        self._i2c.readfrom_into(self._address, crc_result)
        result = []
        for i in range(reply_size):
            word = [crc_result[3 * i], crc_result[3 * i + 1]]
            crc = crc_result[3 * i + 2]
            if self._generate_crc(word) != crc:
                raise RuntimeError("CRC Error")
            result.append(word[0] << 8 | word[1])
        return result

    def _generate_crc(self, data: bytearray) -> int:
        crc = _SGP30_CRC8_INIT
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ _SGP30_CRC8_POLYNOMIAL
                else:
                    crc <<= 1
        return crc & 0xFF