import time
import socket
import argparse
import traceback


class Client:
    def __init__(self, args):
        self.dest = (args.server_ip, args.server_port)
        src_port = 0 if args.client_port is None else args.client_port
        source = ('0.0.0.0', src_port)

        # UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(source)

        self.current_packet = b''
        self.period = 1 / args.test_hz
        self.last_tx = time.time()
        self.test_pak_size = args.pac_size

    def start(self):
        while True:
            try:
                if time.time() - self.last_tx > self.period:
                    self.last_tx = time.time()
                    self.make_packet('t' * self.test_pak_size)  # Form packet
                    self.outbound()  # Send packet

            except KeyboardInterrupt:
                print('Gracefully shutting down...')
                self.end()

    def outbound(self):
        try:
            self.sock.sendto(self.current_packet, self.dest)
            return True
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            print('\n\n^^^^^^^^^\nFailed to send message. Please try again later')
            return False

    def make_packet(self, message):
        self.current_packet = message.encode('ascii')

    def end(self):
        self.sock.close()
        exit()


# Main method to read command line arguments
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', dest='server_ip', action='store', required=True,
                        help='Server IP Address', type=str)
    parser.add_argument('--port', dest='server_port', action='store', required=False,
                        help='Server Port', type=int)
    parser.add_argument('--client_port', dest='client_port', action='store', required=False,
                        help='Client Port', type=int)
    parser.add_argument('--hz', dest='test_hz', action='store', required=True,
                        help='Test rate', type=int)
    parser.add_argument('--size', dest='pac_size', action='store', required=False,
                        help='Number of bytes per packet', type=int)
    args = parser.parse_args()

    tester = Client(args)
    tester.start()


if __name__ == "__main__":
    main()
