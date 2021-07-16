import time
import serial
import serial.tools.list_ports as list_ports


def list_devices(product=('UWB', 'Pozyx', 'STM32 Virtual ComPort', 'nRF52 USB Demo'),
                 manufacturer=('Silicon Labs'),
                 verbose=False):
    """ Returns {Serial number: Serial path}"""
    ports = list_ports.comports()
    if verbose:
        print('Discovered {} serial port(s):'.format(len(ports)))
        for port in ports:
            print('{}: {} - <{}>, {}'.format(port.device, port.manufacturer, port.description, port.serial_number))
    boards = []
    for i in product:
        boards += [x for x in ports if x.description is not None and x.description.startswith(i)]
    for i in manufacturer:
        boards += [x for x in ports if x.manufacturer is not None and x.manufacturer.startswith(i)]
    return {i.serial_number: i.device for i in boards}


if __name__ == '__main__':
    device = list_devices()
    assert len(device) == 1
    device = list(device.values())[0]
    print(f'Connecting to {device}...')

    counter = 0
    with serial.Serial(device, baudrate=115200) as ser:
        with open('bench_clock.log', 'ab') as f:
            while True:
                try:
                    line_b = ser.readline()
                    line_b = f'{time.time()}\t'.encode('utf-8') + line_b
                    try:
                        counter += 1
                        if counter % 1000 == 0:
                            print(line_b.decode('utf-8'), end='')
                    except UnicodeDecodeError:
                        print('Decode Error:', end='\t')
                        print(line_b)
                    f.write(line_b)
                except KeyboardInterrupt:
                    print('Closing connection...')
                    break
