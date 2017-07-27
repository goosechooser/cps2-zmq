import sys
import argparse
from cps2_zmq.gather.MameServer import MameServer

def parse_args(args):
    parser = argparse.ArgumentParser(description='starts a MameServer process')
    parser.add_argument('address', type=str,
                        help='address to bind')
    parser.add_argument('port', type=int,
                        help='port to open')
    parser.add_argument('-o', '--output', action='store_true',
                        help='specify whether to log to a file or not')


    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])

    front_addr = ':'.join([args.address, str(args.port)])
    worker_addr = ':'.join([args.address, str(args.port + 1)])

    try:
        server = MameServer(front_addr, worker_addr, args.output)
    except Exception as err:
        print(err)
    else:
        server.start()
        server.report()
        server.shutdown()

        sys.exit(0)

if __name__ == '__main__':
    main()
