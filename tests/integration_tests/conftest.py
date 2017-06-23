# pylint: disable=E1101

from threading import Thread
import pytest
import zmq
import msgpack

class MockMameServer(Thread):
    def __init__(self, port, context=None):
        super(MockMameServer, self).__init__()
        self._context = context or zmq.Context.instance()
        self._publisher = self._context.socket(zmq.PUB)
        self._publisher.bind(':'.join(["tcp://127.0.0.1", str(port)]))
        self._msg_limit = 10

    @property
    def msg_limit(self):
        return self._msg_limit

    @msg_limit.setter
    def msg_limit(self, value):
        self._msg_limit = value

    def run(self):
        pass

    def close(self):
        self._publisher.close()

@pytest.fixture(scope="module")
def server():
    server = MockMameServer(5666)
    yield server
    server.close()
