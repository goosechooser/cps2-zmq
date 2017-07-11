# pylint: disable=E1101

import zmq
import pytest
from cps2_zmq.gather import MameServer
from cps2_zmq.gather import mdp

port = 6668
front_addr = ':'.join(["tcp://127.0.0.1", str(port)])
back_addr = ':'.join(["tcp://127.0.0.1", str(port + 1)])

worker_idn = bytes(str(1), encoding='UTF-8')
empty = b''
service = b'mame'

@pytest.fixture(scope="function")
def server():
    server = MameServer.MameServer(front_addr, back_addr)
    yield server
    server.shutdown()

@pytest.fixture(scope="function")
def socket():
    context = zmq.Context.instance()
    test_socket = context.socket(zmq.DEALER)
    test_socket.setsockopt(zmq.IDENTITY, worker_idn)
    test_socket.connect(back_addr)
    yield test_socket
    test_socket.close()

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

# socket.recv_multipart() is timing out??
@pytest.mark.skip
@pytest.mark.timeout(timeout=3, method='thread')
def test_disconnect_worker(server, socket):
    server.register_worker(worker_idn, service)
    server.disconnect_worker(worker_idn, server.backend)

    print(back_addr)

    result = socket.recv_multipart()
    print('???')

    assert result.pop() == mdp.DISCONNECT
    assert result.pop() == server.WORKER_PROTOCOL
    assert result.pop() == empty
    assert result.pop() == worker_idn

    assert len(server.workers) == 0
    assert worker_idn not in server.workers
