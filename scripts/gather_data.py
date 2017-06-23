# pylint: disable=E1101
"""
Grabs the raw json data from a MAME instance.
Writes it to a file.
"""

import os
import json
import zmq

def print_raw_data(folder, message):
    fnum = str(message['frame_number'])
    fname = '_'.join(['frame', fnum, 'data.json'])
    fpath = '\\'.join([folder, fname])

    enc = json.dumps(message)
    
    with open(fpath, 'w') as f:
        f.write(enc)

def main(port):
    context = zmq.Context.instance()

    addr = "tcp://localhost"
    serversub = context.socket(zmq.SUB)
    serversub.connect(':'.join([addr, str(port)]))
    serversub.setsockopt_string(zmq.SUBSCRIBE, '')

    working = True
    print('running')
    dropped = 0
    while working:
        try:
            message = serversub.recv_json()
        except UnicodeDecodeError:
            dropped += 1

        if message['frame_number'] != 'closing':
            print_raw_data('production_data', message)
        else:
            working = False

    serversub.close()
    print('done - dropped', dropped, 'frames')

if __name__ == '__main__':
    main(5556)
