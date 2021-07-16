import utime
import usocket as socket

from util import MPU6050_I2C

SERVER_IP = '192.168.8.144'
SERVER_PORT = 8000
TX_HZ = 200

# Note: Ticks roll over at 2^30. Use utime.ticks_add or utime.ticks_diff instead of + / - to avoid issues

imu = MPU6050_I2C()


class Client:
    def __init__(self):
        self.dest = (SERVER_IP, SERVER_PORT)
        src_port = 0
        source = ('0.0.0.0', src_port)

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(source)

        self.current_packet = b''

        self.tx_period = 1e6 / TX_HZ
        self.tx_next = utime.ticks_us()

        self.stat_next = utime.ticks_us()
        self.counter = 0
        self.counter_last = 0

    def statistics(self):
        self.counter += 1
        if utime.ticks_diff(self.stat_next, utime.ticks_us()) <= 0:
            self.stat_next = utime.ticks_add(self.stat_next, 1e6)
            print('%d Hz' % (self.counter - self.counter_last))
            self.counter_last = self.counter

    def start(self):
        while True:
            if utime.ticks_diff(self.tx_next, utime.ticks_us()) > 0:
                continue

            try:
                self.tx_next += utime.ticks_add(self.tx_next, self.tx_period)
                self.current_packet = imu.data
                self.outbound()  # Send packet
                self.statistics()

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
