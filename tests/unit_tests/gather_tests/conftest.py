# pylint: disable=E1101

import time
import pytest
import zmq
import msgpack


class MockClient():
    def __init__(self, pushto):
        self._context = zmq.Context.instance()

        self._pusher = self._context.socket(zmq.PUSH)
        self._pusher.bind(pushto)
        self._pusher.setsockopt(zmq.LINGER, 0)

    @property
    def pusher(self):
        return self._pusher

    # def _wrap_messages(self, messages):
    #     return [{'frame_number': msg[0], 'sprites': [msg[1]], 'palettes': [msg[2]]} for msg in messages]

    def close(self):
        self._pusher.close()

    def push_messages(self, messages):
        # wrapped = self._wrap_messages(messages)
        messages.append({'frame_number': 'closing', 'sprites': [], 'palettes': []})
        for msg in messages:
            packed = msgpack.packb(msg)
            self._pusher.send(packed)


class MockSink():
    def __init__(self, pullfrom):
        self._context = zmq.Context.instance()

        self._puller = self._context.socket(zmq.PULL)
        self._puller.bind(pullfrom)
        self._puller.setsockopt(zmq.LINGER, 0)

        self._control = self._context.socket(zmq.PUB)
        self._control.bind("inproc://control")

    def run(self, num_messages):
        msgs_recv = 0
        messages = []
        working = True
        while msgs_recv != num_messages:
            message = self._puller.recv_pyobj()
            if message == 'closing':
                self._control.send_string('KILL')
            else:
                messages.append(message)
                msgs_recv += 1

        self._control.close()
        return messages

@pytest.fixture(scope="module")
def client():
    return MockClient("inproc://toworkers")

@pytest.fixture(scope="module")
def sink():
    return MockSink("inproc://fromworkers")
