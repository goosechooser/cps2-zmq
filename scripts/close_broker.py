# pylint: disable=E1101
"""
Quick script to close the broker.
"""
import sys
import zmq

def close_broker(port, addr="tcp://127.0.0.1", type=zmq.DEALER):
    context = zmq.Context.instance()
    socket = context.socket(type)
    socket.setsockopt(zmq.LINGER, 5)
    socket.setsockopt(zmq.IDENTITY, b'closer')
    address = ':'.join([addr, str(port)])
    socket.connect(address)

    print('Connected to', address)
    message = [b"", b"MDPC01", b"disconnect", b"closing"]
    print('Sending', message)
    socket.send_multipart(message)
    print('Closing')
    socket.close()

if __name__ == '__main__':
    port = 5556
    if len(sys.argv) > 1:
        port = sys.argv[1]

    close_broker(port)
