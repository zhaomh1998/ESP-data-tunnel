import utime
import usocket as socket

import mac
from util import MPU6050_I2C

SERVER_IP = '192.168.8.144'
SERVER_PORT = 8000
TX_HZ = 200

# Note: Specific to firmware esp8266-20200911-v1.13.bin, ticks roll over at 2^30.
# Use utime.ticks_add or utime.ticks_diff instead of + / - to avoid issues
# This number may differ on other versions of firmware or other MCUs.

imu = MPU6050_I2C()


class Client:
    def __init__(self):
        self.dest = (SERVER_IP, SERVER_PORT)
        src_port = 8000
        source = ('0.0.0.0', src_port)

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind(source)

        self.current_packet = b''

        self.tx_period = int(1e6 / TX_HZ)
        self.tx_next = utime.ticks_us()

        self.stat_next = utime.ticks_us()
        self.counter = 0
        self.counter_last = 0

        # Handles microsecond tick overflows (per 17.9 minutes)
        # TODO: millisecond tick overflow not handled (per 12.4 days)
        self.last_us = utime.ticks_us()
        self.us_overflows = 0

        # Loss benchmark
        self.bench_tx_hz_min = 50
        self.bench_tx_hz_max = 350
        self.bench_tx_hz_step = 5
        self.bench_tx_hz = self.bench_tx_hz_min
        self.bench_packets_per_rate = 500
        self.bench_tx_sent = 0

    def statistics(self):
        self.counter += 1
        if utime.ticks_diff(self.stat_next, utime.ticks_us()) <= 0:
            self.stat_next = utime.ticks_add(self.stat_next, int(1e6))
            print('%d Hz' % (self.counter - self.counter_last))
            self.counter_last = self.counter

    def true_us(self):
        return utime.ticks_us() + self.us_overflows

    def handle_us_overflow(self):
        current_us = utime.ticks_us()
        if current_us < self.last_us:
            self.us_overflows += 1073741824  # Specific to esp8266-20200911-v1.13.bin. May differ on other FW / MCUs.
        self.last_us = current_us

    def start(self):
        while True:
            if utime.ticks_diff(self.tx_next, utime.ticks_us()) > 0:
                continue

            try:
                self.tx_next = utime.ticks_add(self.tx_next, self.tx_period)
                self.handle_us_overflow()

                self.inbound()
                self.make_data_packet()
                self.outbound()  # Send packet
                self.statistics()

            except KeyboardInterrupt:
                print('Gracefully shutting down...')
                self.end()

    def make_data_packet(self):
        imu_data = imu.data  # 14B
        ts = self.true_us().to_bytes(5, 'big', False)  # 5B
        reserved = bytearray([0, 0, 0])  # 3B
        # 14 + 5 + 3 = 22 Bytes
        self.current_packet = imu_data + ts + reserved

    def inbound(self, buf_size=4096):
        try:
            data, client_addr = self.sock.recvfrom(buf_size)
            reply = mac.process_command(data, self)
            if reply is not None:
                self.sock.sendto(reply, client_addr)
            return True, client_addr, data
        except OSError:
            # Nothing received
            return False, None, None

    def outbound(self):
        self.sock.sendto(self.current_packet, self.dest)

    def end(self):
        self.sock.close()
        exit()

    # -------------------- MAC --------------------
    def mac_sync(self):
        print('SYNC!')

    def update_conf(self, new_conf):
        print('Update Conf with ' + repr(new_conf))

    # -------------------- Benchmarks --------------------
    def benchmark_clock(self):
        while True:
            self.handle_us_overflow()
            us = utime.ticks_us()
            us_t = self.true_us()
            ms = utime.ticks_ms()
            s = utime.time()
            print('%d\t%d\t%d\t%d' % (us_t, us, ms, s))

    def benchmark_loss(self):
        while True:
            if utime.ticks_diff(self.tx_next, utime.ticks_us()) > 0:
                continue

            try:
                period = int(1e6 / self.bench_tx_hz)
                self.tx_next = utime.ticks_add(self.tx_next, period)
                self.handle_us_overflow()

                self.make_data_packet_benchmark()
                self.outbound()  # Send packet
                self.bench_tx_sent += 1
                if self.bench_tx_sent % self.bench_packets_per_rate == 0:
                    self.bench_tx_hz += self.bench_tx_hz_step
                    if self.bench_tx_hz > self.bench_tx_hz_max:
                        self.bench_tx_hz = self.bench_tx_hz_min
                self.statistics()

            except KeyboardInterrupt:
                print('Gracefully shutting down...')
                self.end()

    def make_data_packet_benchmark(self):
        imu_data = imu.data  # 14B
        ts = self.true_us().to_bytes(5, 'big', False)  # 5B
        tx_rate = self.bench_tx_hz.to_bytes(2, 'big', False)  # 2B
        reserved = bytearray([0])  # 1B
        # 14 + 5 + 3 = 22 Bytes
        self.current_packet = imu_data + ts + tx_rate + reserved


tester = Client()
tester.start()
# tester.benchmark_clock()
# tester.benchmark_loss()
