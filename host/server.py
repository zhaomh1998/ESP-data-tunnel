import time
import json
import socket
import argparse
import traceback

from decode import decode_tag_packet, decode_tag_packet_bench

import schedule

# https://stackoverflow.com/a/1267524
my_ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
    [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
     [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]])
assert len(my_ip) >= 1, 'Cannot find own IP Address'
my_ip = my_ip[0]
print(f'Server on {my_ip}')


class Server:
    def __init__(self, args, **kwargs):
        self.addr = ('0.0.0.0', args['server_port'] if isinstance(args, dict) else args.server_port)

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setblocking(False)
        self.sock.bind(self.addr)

        self.counter = dict()
        self.new_packet = dict()
        self.counter_last = self.counter.copy()
        self.last_stat = time.time()

        self.job_mac = None
        self.job_ping = None
        self.job_stat = schedule.every(2).seconds.do(self.statistics)

        self.nodes = dict()

    # -------------------- Server Operations --------------------

    def start(self):
        print('Server listening on %s:%s' % self.addr)
        while True:
            try:
                schedule.run_pending()
                self.inbound()
            except KeyboardInterrupt:
                self.shutdown()

    def shutdown(self):
        self.sock.close()
        print('\nServer shutting down')
        exit()

    def statistics(self):
        t_since_last = time.time() - self.last_stat
        self.last_stat = time.time()
        for client in self.counter.keys():
            if client in self.counter_last.keys():
                rate = int((self.counter[client] - self.counter_last[client]) / t_since_last)
                print('[%s:%s] ' % client + f'{rate} Hz | ' + self.new_packet[client])
        self.counter_last = self.counter.copy()

    def inbound(self, buf_size=4096):
        # Retrieve packet
        try:
            data, client_addr = self.sock.recvfrom(buf_size)
            if client_addr[0] == my_ip:
                # Ignore own packet
                return False, None, None
        except KeyboardInterrupt:
            raise
        except BlockingIOError:
            # Nothing received
            return False, None, None
        except:
            traceback.print_exc()
            print('\n\n^^^^^^^^^\nFailed to receive packet.')
            return False, None, None

        # Handle packet
        try:
            packet = data.decode('ascii')
        except UnicodeDecodeError:
            # Binary data packet
            self.handle_binary_packet(client_addr, data)
            return

        try:
            parsed = json.loads(packet)
            if 'cmd' in parsed.keys():
                self.handle_mac_packet(client_addr, parsed)
            else:
                self.handle_plain_text_packet(client_addr, packet)
        except json.decoder.JSONDecodeError:
            # Plain text non json
            self.handle_plain_text_packet(client_addr, packet)

    def outbound(self, packet, addr=('255.255.255.255', 8000)):
        """ Send packets out. If addr not specified, broadcast packet """
        # Prepare packet
        if isinstance(packet, dict):
            packet = json.dumps(packet).encode('ascii')
        elif isinstance(packet, str):
            packet = packet.encode('ascii')
        assert isinstance(packet, bytes)

        try:
            self.sock.sendto(packet, addr)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            print('\n\n^^^^^^^^^\nFailed to send packet. Network issue?')

    # ----------------- Inbound Packet Handlers -----------------

    def handle_mac_packet(self, addr, packet):
        pass

    def handle_binary_packet(self, addr, data):
        tag_data = decode_tag_packet(data)
        with open('rx.log', 'a') as f:
            f.write(','.join('{:8.2f}'.format(i) for i in decode_tag_packet_bench(data)))
            f.write('\n')
        packet = '\t'.join('{:8.2f}'.format(i) for i in tag_data)
        self.new_packet[addr] = packet

        # Statistics
        if addr in self.counter.keys():
            self.counter[addr] += 1
        else:
            self.counter[addr] = 1

    def handle_plain_text_packet(self, addr, packet):
        print('[%s:%s] ' % addr + packet)

    # --------------------------- MAC ---------------------------

    def ping(self):
        self.outbound({'cmd': 'ping'})

    def mac_sync(self):
        self.outbound({'cmd': 'sync'})

    def set_mac_interval(self, interval_s):
        if self.job_mac is not None:
            schedule.cancel_job(self.job_mac)
        self.job_mac = schedule.every(interval_s).seconds.do(self.mac_sync)

    def set_ping_interval(self, interval_s):
        if self.job_ping is not None:
            schedule.cancel_job(self.job_ping)
        self.job_ping = schedule.every(interval_s).seconds.do(self.ping)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', dest='server_port', action='store', required=True,
                        help='Server Port', type=int)
    args = parser.parse_args()

    receiver = Server(args)
    receiver.start()


if __name__ == "__main__":
    main()
