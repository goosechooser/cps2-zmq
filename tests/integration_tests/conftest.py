# pylint: disable=E1101

import time
from threading import Thread
import pytest
import zmq
import msgpack

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
            self._publisher.send(data)

        self._publisher.send(msgpack.packb(closing))

    def close(self):
        self._publisher.close()

@pytest.fixture(scope="module")
def client(rawframes):
    client = MockMameClient(5666, rawframes)
    yield client
    client.close()
