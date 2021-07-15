from machine import Pin, I2C
import math
import time


class ADXL345_SPI:
    SPI_READ = 1 << 7
    SPI_MULTIPLE_BYTES = 1 << 6
    ADXL345_DATAX0 = 0x32

    # https://github.com/DFRobot/micropython-dflib/blob/master/ADXL345/user_lib/ADXL345.py
    def __init__(self, hspi, cs):
        self.spi = hspi
        self.cs = cs

        self.spi_write(b'\x31\x07')  # SPI 4-wire Mode
        self.spi_write(b'\x2c\x0a')  # 100Hz, disable low power
        self.spi_write(b'\x2e\x00')  # Disable all interrupts
        self.spi_write(b'\x38\x00')  # Disable FIFO
        self.spi_write(b'\x2d\x08')  # Start measuring

    def spi_write(self, write_buf):
        self.cs.value(0)
        self.spi.write(write_buf)
        self.cs.value(1)

    def spi_read(self, addr, read_buf):
        self.cs.value(0)
        if len(read_buf) > 1:
            addr = self.SPI_READ | self.SPI_MULTIPLE_BYTES | addr
        else:
            addr = self.SPI_READ | addr
        self.spi.readinto(read_buf, addr)
        self.cs.value(1)
        return read_buf

    @property
    def xyz(self):
        # Ported from official AXDL345 library C code
        # https://github.com/analogdevicesinc/no-OS/blob/master/drivers/accel/adxl345/adxl345.c#L214
        buff = bytearray(7)
        self.spi_read(self.ADXL345_DATAX0, buff)
        x = (buff[2] << 8) | buff[1]
        y = (buff[4] << 8) | buff[3]
        z = (buff[6] << 8) | buff[5]
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        return x, y, z

    @property
    def orientation(self):
        # https://wiki.dfrobot.com/How_to_Use_a_Three-Axis_Accelerometer_for_Tilt_Sensing
        x, y, z = self.xyz
        roll = math.atan2(y, z) * 57.3
        pitch = math.atan2((- x), math.sqrt(y * y + z * z)) * 57.3
        return roll, pitch


class ADXL345_I2C:
    # https://github.com/DFRobot/micropython-dflib/blob/master/ADXL345/user_lib/ADXL345.py
    def __init__(self, addr=0x53):
        self.addr = addr
        self.i2c = I2C(-1, Pin(5), Pin(4))
        b = bytearray(1)
        b[0] = 0
        self.i2c.writeto_mem(self.addr, 0x2d, b)
        b[0] = 16
        self.i2c.writeto_mem(self.addr, 0x2d, b)
        b[0] = 8
        self.i2c.writeto_mem(self.addr, 0x2d, b)

        self.buff = bytearray(6)

    @property
    def xyz(self):
        self.buff = self.i2c.readfrom_mem(self.addr, 0x32, 6)
        x = (int(self.buff[1]) << 8) | self.buff[0]
        y = (int(self.buff[3]) << 8) | self.buff[2]
        z = (int(self.buff[5]) << 8) | self.buff[4]
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        return x, y, z

    @property
    def xyz_raw(self):
        self.buff = self.i2c.readfrom_mem(self.addr, 0x32, 6)
        return self.buff
