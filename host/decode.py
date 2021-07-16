def to_int16(msb, lsb):
    return int.from_bytes(bytearray([msb, lsb]), byteorder='big', signed=True)


def decode_adxl345_packet(buff):
    assert isinstance(buff, bytes)
    assert len(buff) == 6

    x = (int(buff[1]) << 8) | buff[0]
    y = (int(buff[3]) << 8) | buff[2]
    z = (int(buff[5]) << 8) | buff[4]
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    if z > 32767:
        z -= 65536
    return x, y, z


def decode_mpu6050_packet(buff):
    assert isinstance(buff, bytes)
    assert len(buff) == 14

    acc_x = to_int16(buff[0], buff[1])
    acc_y = to_int16(buff[2], buff[3])
    acc_z = to_int16(buff[4], buff[5])
    temperature = to_int16(buff[6], buff[7]) / 340.00 + 36.53
    gyro_x = to_int16(buff[8], buff[9])
    gyro_y = to_int16(buff[10], buff[11])
    gyro_z = to_int16(buff[12], buff[13])
    return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temperature


def decode_tag_packet(buff):
    assert isinstance(buff, bytes)
    assert len(buff) == 22
    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temperature = decode_mpu6050_packet(buff[:14])
    time_us = int.from_bytes(buff[14:14 + 5], byteorder='big', signed=False)
    reserved = buff[14 + 5:]
    return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temperature, time_us
