import sys
import argparse
from cps2_zmq.gather.MameWorker import MameWorker

def parse_args(args):
    parser = argparse.ArgumentParser(description='starts a MameWorker process')
    parser.add_argument('idn', type=str,
                        help='worker id number')
    parser.add_argument('address', type=str,
                        help='address to connect to')
    parser.add_argument('port', type=int,
                        help='port to connect')
    parser.add_argument('--pub', action='store_true',
                        help='whether to publish results of work or not')
    parser.add_argument('-o', '--output', action='store_true',
                        help='specify whether to log to a file or not')


    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])

    addr = ':'.join([args.address, str(args.port)])

    if args.pub:
        pub_addr = ':'.join([args.address, str(args.port + 1)])
    else:
        pub_addr = None

    try:
        worker = MameWorker(args.idn, addr, b'mame', pub_addr, log_to_file=args.output)
    except Exception as err:
        print(err)
    else:
        worker.start()
        worker.report()
        worker.close()

        sys.exit(0)

if __name__ == '__main__':
    main()

# worker = MameWorker(str(random.randint(69, 420)), "tcp://127.0.0.1:5557", b'mame', pub_addr="tcp://127.0.0.1:5558")
