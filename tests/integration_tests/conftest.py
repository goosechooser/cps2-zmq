# pylint: disable=E1101

import sys
import time
from threading import Thread
import pytest
import zmq

# Need to refactor this to pull from not mongodb
class MockMameClient(Thread):
    def __init__(self, port, msgs, context=None):
        super(MockMameClient, self).__init__()
        self._context = context or zmq.Context.instance()
        self.front = self._context.socket(zmq.DEALER)
        self.front.connect(':'.join(["tcp://127.0.0.1", str(port)]))
        self.front.setsockopt(zmq.IDENTITY, b'\x69')
        self.msgs = msgs
        self.daemon = True

    def run(self):
        print('Client sending frames')
        sys.stdout.flush()

        for frame in self.msgs:
            self.request(b'mame', frame)

        time.sleep(5)
        print('Client disconnecting')
        sys.stdout.flush()
        self.request(b'disconnect', b'MENSA')

    def request(self, service, message):
        self.front.send_multipart([b'', b'MDPC01', service, message])

    def close(self):
        self.front.close()

@pytest.fixture(scope="module")
def client(rawframes):
    client = MockMameClient(5666, rawframes)
    yield client
    client.close()
