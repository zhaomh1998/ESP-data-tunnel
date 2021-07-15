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
