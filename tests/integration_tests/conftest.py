# pylint: disable=E1101

import sys
import time
import os
import os.path
from threading import Thread
import pytest
import zmq
import msgpack
from cps2_zmq.process import Frame

def get_file(fpath):
    with open(os.path.normpath(fpath), 'r+b') as f:
        return f.read()

@pytest.fixture(scope='module') 
def rawframes():
    data_dir = os.path.normpath('tests/test_data/raw_frame_data/')
    frames = [get_file(os.path.join(data_dir, f)) for f in sorted(os.listdir(data_dir))]
    return frames

# Need to refactor this to pull from not mongodb
class MockMameClient(Thread):
    def __init__(self, port, msgs, context=None):
        super(MockMameClient, self).__init__()
        self._context = context or zmq.Context.instance()
        self._publisher = self._context.socket(zmq.PUB)
        self._publisher.connect(':'.join(["tcp://127.0.0.1", str(port)]))
        self.msgs = msgs
        self.daemon = True
    
    def run(self):
        time.sleep(5)
        closing = {'frame_number': 'closing'}

        for frame in self.msgs:
            data = frame
            # print(data)
            # sys.stdout.flush()
            self._publisher.send(data)

        self._publisher.send(msgpack.packb(closing))

    def close(self):
        self._publisher.close()

@pytest.fixture(scope="module")
def client(rawframes):
    client = MockMameClient(5666, rawframes)
    yield client
    client.close()
