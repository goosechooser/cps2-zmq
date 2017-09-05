import sys
import argparse
from cps2zmq.gather.LogSink import LogSink


def parse_args(args):
    parser = argparse.ArgumentParser(description='starts a LogSink process')
    parser.add_argument('idn', type=str,
                        help='worker id number')
    parser.add_argument('address', type=str,
                        help='address to connect to')
    parser.add_argument('port', type=int,
                        help='port to connect')
    parser.add_argument('--topics', type=str, nargs='*',
                        help='topics to listen to')
    parser.add_argument('-o', '--output', action='store_true',
                        help='specify whether to log to a file or not')

    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])
    addr = ':'.join([args.address, str(args.port)])
    sub_addr = ':'.join([args.address, str(args.port + 1)])

    try:
        sink = LogSink(args.idn, addr, sub_addr, args.topics, log_to_file=args.output)
    except Exception as err:
        print(err)
    else:
        sink.start()
        sink.report()
        sink.close()

        sys.exit(0)

if __name__ == '__main__':
    main()
# sink = LogSink("1", "tcp://127.0.0.1:5557", "tcp://127.0.0.1:5558", ['MameWorker'], log_to_file=True)
