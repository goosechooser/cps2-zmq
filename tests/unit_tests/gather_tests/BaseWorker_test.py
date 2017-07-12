# pylint: disable=E1101

import pytest
import zmq
from cps2_zmq.gather.BaseWorker import BaseWorker
from cps2_zmq.gather import mdp

port = 6666
addr = ':'.join(["tcp://127.0.0.1", str(port)])

empty = b''
service = b'mame'

@pytest.fixture(scope='function')
def worker():
    w = BaseWorker(str(1), addr, b'base')
    yield w
    w.close()

@pytest.fixture(scope="function")
def socket():
    context = zmq.Context.instance()
    test_socket = context.socket(zmq.ROUTER)
    test_socket.bind(addr)
    yield test_socket
    test_socket.close()

# only tests disconnect case atm
def test_handle_message(worker):
    test_msg = [b'', b'MDPW01', mdp.DISCONNECT]
    worker.handle_message(test_msg)

    assert worker.heartbeater == None
    assert worker.frontstream == None

def test_ready(worker, socket):
    worker.ready(worker.frontstream.socket, service)
    result = socket.recv_multipart()

    assert result.pop(0) == worker.idn
    assert result.pop(0) == empty
    assert result.pop(0) == worker._protocol
    assert result.pop(0) == mdp.READY
    assert result.pop(0) == service
    assert worker.current_liveness == worker.HB_LIVENESS

def test_reply(worker, socket):
    client_addr = b'client'
    message = b'test message'
    worker.reply(worker.frontstream.socket, client_addr, message)
    result = socket.recv_multipart()

    assert result.pop(0) == worker.idn
    assert result.pop(0) == empty
    assert result.pop(0) == worker._protocol
    assert result.pop(0) == mdp.REPLY
    assert result.pop(0) == client_addr
    assert result.pop(0) == empty
    assert result.pop(0) == message

def test_heartbeat(worker, socket):
    worker.ready(worker.frontstream.socket, service)
    socket.recv_multipart()
    worker.heartbeat(worker.frontstream.socket)
    result = socket.recv_multipart()

    assert result.pop(0) == worker.idn
    assert result.pop(0) == empty
    assert result.pop(0) == worker._protocol
    assert result.pop(0) == mdp.HEARTBEAT
    assert worker.current_liveness == worker.HB_LIVENESS - 1

def test_disconnect(worker, socket):
    worker.disconnect(worker.frontstream.socket)
    result = socket.recv_multipart()

    assert result.pop(0) == worker.idn
    assert result.pop(0) == empty
    assert result.pop(0) == worker._protocol
    assert result.pop(0) == mdp.DISCONNECT
