# pylint: disable=E1101

from threading import Thread
import pytest
import zmq
import pymongo
import msgpack

class MockMameClient(Thread):
    def __init__(self, port, collection, context=None):
        super(MockMameClient, self).__init__()
        self._context = context or zmq.Context.instance()
        self._publisher = self._context.socket(zmq.PUB)
        self._publisher.bind(':'.join(["tcp://127.0.0.1", str(port)]))
        self._msg_limit = 10
        self._client = pymongo.MongoClient()
        self._db = self._client[collection]
        self.daemon = True

    @property
    def msg_limit(self):
        return self._msg_limit

    @msg_limit.setter
    def msg_limit(self, value):
        self._msg_limit = value

    def run(self):
        frames = self._db.frames.find(projection={'_id' : 0}, limit=self.msg_limit)
        for frame in frames:
            msg = msgpack.packb(frame, encoding='utf-8')
            self._publisher.send(msg)

        msg = msgpack.packb({'frame_number' : 'closing'}, encoding='utf-8')
        self._publisher.send(msg)

    def close(self):
        self._publisher.close()
        self._client.close()

@pytest.fixture(scope="module")
def client():
    client = MockMameClient(5666, 'cps2')
    yield client
    client.close()
