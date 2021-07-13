import time
import socket
import argparse
import traceback


class Server:
    def __init__(self, args):
        self.addr = ('0.0.0.0', args.server_port)

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.addr)

        self.counter = dict()
        self.new_packet = dict()
        self.counter_last = self.counter.copy()
        self.last_stat = time.time()

    def start(self):
        print('Server listening on %s:%s' % self.addr)
        while True:
            try:
                status, source, msg = self.inbound(verbose=False)
                if source in self.counter.keys():
                    self.counter[source] += 1
                else:
                    self.counter[source] = 1
                self.statistics()

            except KeyboardInterrupt:
                self.shutdown()
            except OSError:
                traceback.print_exc()
                self.shutdown()

    def statistics(self):
        if time.time() - self.last_stat > 1:
            self.last_stat = time.time()
            for client in self.counter.keys():
                if client in self.counter_last.keys():
                    pak_last_sec = self.counter[client] - self.counter_last[client]
                    print('[%s:%s] ' % client + f'{pak_last_sec} Hz | ' + self.new_packet[client])
            self.counter_last = self.counter.copy()

    def shutdown(self):
        self.sock.close()
        print('\nServer shutting down')
        exit()

    def reply(self, packet, sender):
        try:
            self.sock.sendto(packet, sender)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            print('\n\n^^^^^^^^^\nFailed to send reply. Network issue?')

    def inbound(self, buf_size=4096, verbose=True):
        try:
            data, client_addr = self.sock.recvfrom(buf_size)
            packet = data.decode('ascii')
            self.new_packet[client_addr] = packet
            if verbose:
                print('[%s:%s] ' % client_addr + packet)
            return True, client_addr, packet
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            print('\n\n^^^^^^^^^\nFailed to receive and decode packet.')
            return False, None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', dest='server_port', action='store', required=True,
                        help='Server Port', type=int)
    args = parser.parse_args()

    receiver = Server(args)
    receiver.start()


if __name__ == "__main__":
    main()
