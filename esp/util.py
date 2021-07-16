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


class MPU6050_I2C():
    MPU6050_PWR_MGMT_1 = 0x6B

    MPU6050_ACCEL_CONFIG = 0x1C
    MPU6050_ACCEL_RANGE_2G = int('00000000', 2)  # Unit: G
    MPU6050_ACCEL_RANGE_4G = int('00001000', 2)
    MPU6050_ACCEL_RANGE_8G = int('00010000', 2)
    MPU6050_ACCEL_RANGE_16G = int('00011000', 2)

    MPU6050_GYRO_CONFIG = 0x1B
    MPU6050_GYRO_RANGE_250 = int('00000000', 2)  # Unit: deg/s
    MPU6050_GYRO_RANGE_500 = int('00001000', 2)
    MPU6050_GYRO_RANGE_1000 = int('00010000', 2)
    MPU6050_GYRO_RANGE_2000 = int('00011000', 2)

    def __init__(self, addr=0x68):
        self.addr = addr
        self.i2c = I2C(-1, Pin(5), Pin(4))
        self.write_reg(self.MPU6050_PWR_MGMT_1, 0)
        self.write_reg(self.MPU6050_ACCEL_CONFIG, self.MPU6050_ACCEL_RANGE_2G)
        self.write_reg(self.MPU6050_GYRO_CONFIG, self.MPU6050_GYRO_RANGE_250)

    def write_reg(self, addr, byte):
        self.i2c.writeto_mem(self.addr, addr, bytearray([byte]))

    @property
    def data(self):
        return self.i2c.readfrom_mem(self.addr, 0x3B, 14)

    def to_int16(self, msb, lsb):
        """ Converts to signed int16 from two bytes """
        data = int.from_bytes(bytearray([msb, lsb]), 'big')
        if data > 32767:
            data -= 65536
        return data

    @property
    def raw_readings(self):
        """ Returns raw readings in [-32768, +32767] for accelerometer and gyroscope, scaled reading for temperature"""
        raw_bytes = self.data

        acc_x = self.to_int16(raw_bytes[0], raw_bytes[1])
        acc_y = self.to_int16(raw_bytes[2], raw_bytes[3])
        acc_z = self.to_int16(raw_bytes[4], raw_bytes[5])
        temperature = self.to_int16(raw_bytes[6], raw_bytes[7]) / 340.00 + 36.53
        gyro_x = self.to_int16(raw_bytes[8], raw_bytes[9])
        gyro_y = self.to_int16(raw_bytes[10], raw_bytes[11])
        gyro_z = self.to_int16(raw_bytes[12], raw_bytes[13])

        return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temperature
