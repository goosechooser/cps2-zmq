# pylint: disable=E1101

import zmq
import pytest
from cps2_zmq.gather import MameServer
from cps2_zmq.gather import mdp

port = 6668
front_addr = ':'.join(["tcp://127.0.0.1", str(port)])
back_addr = ':'.join(["tcp://127.0.0.1", str(port + 1)])
test_addr = ':'.join(["tcp://127.0.0.1", str(port + 2)])

worker_idn = bytes(str(1), encoding='UTF-8')
empty = b''
service = b'mame'

@pytest.fixture(scope="function")
def server():
    server = MameServer.MameServer(front_addr, back_addr)
    yield server
    server.shutdown()

@pytest.fixture(scope="function")
def bound_socket():
    context = zmq.Context.instance()
    bound_socket = context.socket(zmq.ROUTER)
    bound_socket.bind(test_addr)
    yield bound_socket
    bound_socket.close()

@pytest.fixture(scope="function")
def socket():
    context = zmq.Context.instance()
    socket = context.socket(zmq.DEALER)
    socket.connect(back_addr)
    socket.setsockopt(zmq.IDENTITY, worker_idn)
    yield socket
    socket.close()

def test_register_worker(server):
    server.register_worker(worker_idn, service)

    assert len(server.workers) == 1
    assert len(server.services) == 1

    assert worker_idn in server.workers
    assert service in server.services

def test_unregister_worker(server):
    server.register_worker(worker_idn, service)
    server.unregister_worker(worker_idn)

    assert len(server.workers) == 0
    assert worker_idn not in server.workers

@pytest.mark.timeout(timeout=5, method='thread')
def test_disconnect_worker(server, socket):
    server.register_worker(worker_idn, service)
    server.disconnect_worker(worker_idn, socket)

    result = server.backstream.socket.recv_multipart()

    assert result.pop() == mdp.DISCONNECT
    assert result.pop() == server.WPROTOCOL
    assert result.pop() == empty

    assert len(server.workers) == 0
    assert worker_idn not in server.workers

@pytest.mark.timeout(timeout=5, method='thread')
def test_send_request(server, socket):
    client_addr = b'addr'
    request = b'request'
    server.send_request(socket, worker_idn, client_addr, request)
    result = server.backstream.socket.recv_multipart()

    assert result.pop() == request
    assert result.pop() == empty
    assert result.pop() == client_addr
    assert result.pop() == mdp.REQUEST
    assert result.pop() == server.WPROTOCOL
    assert result.pop() == empty

    assert len(server.workers) == 0
    assert worker_idn not in server.workers

def test_beat(server):
    server.register_worker(worker_idn, service)
    server.beat()
    assert worker_idn in server.workers

    server.workers[worker_idn].current_liveness = -1
    assert server.heartbeater == None
    server.beat()
    assert worker_idn not in server.workers

def handle_backend_ready(server):
    msg = [worker_idn, empty, b'protocol', mdp.READY, service]

    assert len(server.workers) == 1
    assert len(server.services) == 1

    assert worker_idn in server.workers
    assert service in server.services
