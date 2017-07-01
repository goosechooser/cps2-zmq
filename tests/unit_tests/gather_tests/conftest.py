# pylint: disable=E1101

import time
from threading import Thread
import pytest
import zmq
import msgpack

class MockServer():
    def __init__(self, toworkers):
        self.context = zmq.Context.instance()

        self.backend = self.context.socket(zmq.ROUTER)
        self.backend.bind(toworkers)
        self.messages = []

    def close(self):
        self.backend.close()

    def make_messages(self, num):
        self.messages = [msgpack.packb(str(i)) for i in range(num)]

    def close_workers(self, workers):
        empty = b'empty'
        message = b'END'

        for w in workers:
            address = w.w_id
            self.backend.send_multipart([address, empty, message])

    def start(self):
        for msg in self.messages:
            addr, empty, ready = self.backend.recv_multipart()
            print('MockServer received ready')
            multi = [addr, empty, msg]
            print('MockServer sending', multi)
            self.backend.send_multipart(multi)

class MockWorker():
    def __init__(self, wid=None, context=None):
        self._context = context or zmq.Context.instance()
        self.w_id = wid
        self.frontend = self._context.socket(zmq.DEALER)
        self.messages = []
        self.msgs_recv = 0

    def pull_messages(self):
        working = True
        while working:
            message = self._puller.recv_json()
            self.msgs_recv += 1
            if message['frame_number'] == 'closing':
                working = False

    def close(self):
        self.frontend.close()

class MockThreadWorker(Thread):
    def __init__(self, pullfrom="inproc://fromclient", wid=None, context=None):
        super(MockThreadWorker, self).__init__()
        self._context = context or zmq.Context.instance()
        self._w_id = wid
        self._puller = self._context.socket(zmq.PULL)

        self._pusher = self._context.socket(zmq.PUSH)
        self._pusher.setsockopt(zmq.LINGER, 0)
        self._messages = []

    @property
    def w_id(self):
        return self._w_id

    @w_id.setter
    def wid(self, value):
        self._w_id = value

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    def connect_pull(self, pullfrom):
        self._puller.connect(pullfrom)

    def connect_push(self, pushto):
        self._pusher.connect(pushto)

    def setup(self):
        self.daemon = True

    def run(self):
        for message in self._messages:
            # print('thread worker sent', message)
            self._pusher.send_json(message)

    def close(self):
        if not self._puller.closed:
            self._puller.close()
        if not self._pusher.closed:
            self._pusher.close()

class MockClient(Thread):
    def __init__(self, port, context=None):
        super(MockClient, self).__init__()
        self._context = context or zmq.Context.instance()
        self._publisher = self._context.socket(zmq.PUB)
        self._publisher.connect(':'.join(["tcp://127.0.0.1", str(port)]))
        self._msg_limit = 10

    @property
    def msg_limit(self):
        return self._msg_limit

    @msg_limit.setter
    def msg_limit(self, value):
        self._msg_limit = value

    def run(self):
        i = 0
        time.sleep(5)
        while i < self._msg_limit:
            msg = msgpack.packb({'frame_number' : i}, encoding='utf-8')
            self._publisher.send(msg)
            i += 1

        msg = msgpack.packb({'frame_number' : 'closing'}, encoding='utf-8')
        self._publisher.send(msg)
        print('done')

    def close(self):
        self._publisher.close()

@pytest.fixture(scope="function")
def server():
    server = MockServer("inproc://toworkers")
    yield server
    server.close()

@pytest.fixture(scope="module")
def worker():
    worker = MockWorker()
    # worker.pull_from("inproc://tomockworkers")
    yield worker
    worker.close()

@pytest.fixture(scope="module",
                params=[1, 2])
def tworkers(request):
    workers = [MockThreadWorker(wid=i) for i in range(request.param)]
    yield workers
    for w in workers:
        w.close()

@pytest.fixture(scope="module")
def client():
    client = MockClient(5666)
    yield client
    client.close()
