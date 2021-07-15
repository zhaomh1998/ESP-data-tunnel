from machine import RTC, Pin, SPI
import usocket as socket
from util import ADXL345_I2C

SERVER_IP = '192.168.8.144'
SERVER_PORT = 8000

acc = ADXL345_I2C()


class Client:
    def __init__(self):
        self.dest = (SERVER_IP, SERVER_PORT)
        src_port = 0
        source = ('0.0.0.0', src_port)

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(source)

        self.current_packet = b''

    def start(self):
        while True:
            try:
                # acc_data = acc.xyz
                # acc_data = (1, 2, 3)
                # self.make_packet('%.2f, %.2f, %.2f' % acc_data)  # Form packet
                self.make_packet('test')
                # self.make_packet('FAKE 123.45, 123.45, 123.45, 123.45, 123.45, 123.45')
                self.current_packet = acc.xyz_raw
                self.outbound()  # Send packet

            except KeyboardInterrupt:
                print('Gracefully shutting down...')
                self.end()

    def outbound(self):
        self.sock.sendto(self.current_packet, self.dest)

    def make_packet(self, message):
        self.current_packet = message.encode('ascii')

    def end(self):
        self.sock.close()
        exit()


tester = Client()
tester.start()
