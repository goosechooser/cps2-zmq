# pylint: disable=E1101
"""
Grabs the raw packed data from a MAME instance.
Writes it to a file.
"""
import msgpack
import zmq

def print_raw_data(folder, message, msg_num):
    fnum = str(msg_num)
    fname = '_'.join(['frame', fnum, 'data.json'])
    fpath = '\\'.join([folder, fname])

    with open(fpath, 'wb') as f:
        f.write(message)

def main(port):
    context = zmq.Context.instance()

    serversub = context.socket(zmq.SUB)
    serversub.bind(':'.join(["tcp://127.0.0.1", str(port)]))
    serversub.setsockopt_string(zmq.SUBSCRIBE, '')

    working = True
    print('running')
    msgs = 0

    while working:
        message = serversub.recv()
        unpacked = msgpack.unpackb(message, encoding='UTF-8')

        if unpacked['frame_number'] != 'closing':
            print_raw_data('production_data', message, msgs)
            msgs += 1
        else:
            working = False

if __name__ == '__main__':
    main(5556)
