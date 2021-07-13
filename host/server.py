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

    def start(self):
        print('Server listening on %s:%s' % self.addr)
        while True:
            try:
                status, source, msg = self.inbound()
                if source in self.counter.keys():
                    self.counter[source] += 1
                else:
                    self.counter[source] = 1

            except KeyboardInterrupt:
                self.shutdown()
            except OSError:
                traceback.print_exc()
                self.shutdown()

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

    def inbound(self, buf_size=4096):
        try:
            data, client_addr = self.sock.recvfrom(buf_size)
            packet = data.decode('ascii')
            print(packet)
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
