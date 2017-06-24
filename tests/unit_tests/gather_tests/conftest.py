# pylint: disable=E1101

from threading import Thread
import pytest
import zmq
import msgpack

from cps2_zmq.gather.MameSink import MameSink


class MockServer():
    def __init__(self, pushto):
        self._context = zmq.Context.instance()

        self._pusher = self._context.socket(zmq.PUSH)
        self._pusher.bind(pushto)
        self._pusher.setsockopt(zmq.LINGER, 0)

    @property
    def pusher(self):
        return self._pusher

    def close(self):
        self._pusher.close()

    def push_messages(self, messages):
        messages.append({'frame_number': 'closing', 'sprites': [], 'palettes': []})
        for msg in messages:
            packed = msgpack.packb(msg)
            self._pusher.send(packed)


class MockSink(MameSink):
    def __init__(self, pullfrom, workercontrol="inproc://mockcontrol"):
        super(MockSink, self).__init__(pullfrom, workercontrol)
        self._context = zmq.Context.instance()
        self._msg_limit = 10

    @property
    def msg_limit(self):
        return self._msg_limit

    @msg_limit.setter
    def msg_limit(self, value):
        self._msg_limit = value

    def run(self):
        msgs_recv = 0
        messages = []

        while msgs_recv != self._msg_limit:
            recv = self._puller.recv_pyobj()
            if recv['message'] == 'closing':
                self._workerpub.send_string('KILL')
            else:
                messages.append(recv['message'])
                msgs_recv += 1

        return messages

    def close(self):
        self._workerpub.close()
        self._puller.close()

class MockWorker():
    def __init__(self, wid=None, pushto=None, context=None):
        self._context = context or zmq.Context.instance()
        self._wid = wid
        self._pusher = self._context.socket(zmq.PUSH)
        self._pusher.connect(pushto)
        self._messages = []

    @property
    def wid(self):
        return self._wid

    @wid.setter
    def wid(self, value):
        self._wid = value

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    def setup(self):
        pass

    def start(self):
        for message in self._messages:
            self._pusher.send_pyobj(message)

    def close(self):
        self._pusher.close()

class MockThreadWorker(Thread):
    def __init__(self, wid=None, context=None):
        super(MockThreadWorker, self).__init__()
        self._context = context or zmq.Context.instance()
        self._wid = wid
        self._pusher = self._context.socket(zmq.PUSH)
        self._pusher.setsockopt(zmq.LINGER, 0)
        self._messages = []

    @property
    def wid(self):
        return self._wid

    @wid.setter
    def wid(self, value):
        self._wid = value

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    def connect_push(self, pushto):
        self._pusher.connect(pushto)

    def setup(self):
        self.daemon = True

    def run(self):
        for message in self._messages:
            self._pusher.send_pyobj(message)

    def close(self):
        self._pusher.close()

class MockClient(Thread):
    def __init__(self, port, context=None):
        super(MockClient, self).__init__()
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
        i = 0
        # time.sleep(10)
        while i < self._msg_limit:
            print('sending')
            msg = msgpack.packb({'frame_number' : i}, encoding='utf-8')
            self._publisher.send(msg)
            i += 1
            # time.sleep(2)

        msg = msgpack.packb({'frame_number' : 'closing'}, encoding='utf-8')
        self._publisher.send(msg)
        print('done')

    def close(self):
        self._publisher.close()

@pytest.fixture(scope="module")
def server():
    server = MockServer("inproc://toworkers")
    yield server
    server.close()

@pytest.fixture(scope="module")
def sink():
    sink = MockSink("inproc://mockworkers")
    yield sink
    sink.close()

@pytest.fixture(scope="module")
def worker():
    worker = MockWorker(wid=1, pushto="inproc://frommockworkers")
    yield worker
    worker.close()

@pytest.fixture(scope="module")
def workers():
    workers = [MockWorker(wid=1, pushto="inproc://frommockworkers")]
    yield workers
    for w in workers:
        print('worker', w.wid, 'cleanup')
        w.close()

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
