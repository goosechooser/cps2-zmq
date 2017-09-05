# pylint: disable=E1101

import zmq
import pytest
from cps2_zmq.gather import Broker
from cps2_zmq.gather import mdp

port = 6668
front_addr = ':'.join(["tcp://127.0.0.1", str(port)])
back_addr = ':'.join(["tcp://127.0.0.1", str(port + 1)])

worker_idn = bytes(str(1), encoding='UTF-8')
empty = b''
service = b'mame'

@pytest.fixture(scope="function")
def broker():
    broker = Broker(front_addr, back_addr)
    yield broker
    broker.shutdown()

@pytest.fixture(scope="function")
def socket():
    context = zmq.Context.instance()
    socket = context.socket(zmq.DEALER)
    socket.connect(back_addr)
    socket.setsockopt(zmq.IDENTITY, worker_idn)
    yield socket
    socket.close()

def test_register_worker(broker):
    broker.register_worker(worker_idn, service)

    assert len(broker.workers) == 1
    assert len(broker.services) == 1

    assert worker_idn in broker.workers
    assert service in broker.services

def test_unregister_worker(broker):
    broker.register_worker(worker_idn, service)
    broker.unregister_worker(worker_idn)

    assert len(broker.workers) == 0
    assert worker_idn not in broker.workers

@pytest.mark.timeout(timeout=5, method='thread')
def test_disconnect_worker(broker, socket):
    broker.register_worker(worker_idn, service)
    broker.disconnect_worker(worker_idn, socket)

    result = broker.backstream.socket.recv_multipart()

    assert result.pop() == mdp.DISCONNECT
    assert result.pop() == broker.WPROTOCOL
    assert result.pop() == empty

    assert len(broker.workers) == 0
    assert worker_idn not in broker.workers

@pytest.mark.timeout(timeout=5, method='thread')
def test_send_request(broker, socket):
    client_addr = b'addr'
    request = b'request'
    broker.send_request(socket, worker_idn, client_addr, request)
    result = broker.backstream.socket.recv_multipart()

    assert result.pop() == request
    assert result.pop() == empty
    assert result.pop() == client_addr
    assert result.pop() == mdp.REQUEST
    assert result.pop() == broker.WPROTOCOL
    assert result.pop() == empty

    assert len(broker.workers) == 0
    assert worker_idn not in broker.workers

def test_beat(broker):
    broker.register_worker(worker_idn, service)
    broker.beat()
    assert worker_idn in broker.workers

    broker.workers[worker_idn].current_liveness = -1
    assert broker.heartbeater == None
    broker.beat()
    assert worker_idn not in broker.workers

def handle_backend_ready(broker):
    msg = [worker_idn, empty, b'protocol', mdp.READY, service]

    assert len(broker.workers) == 1
    assert len(broker.services) == 1

    assert worker_idn in broker.workers
    assert service in broker.services
