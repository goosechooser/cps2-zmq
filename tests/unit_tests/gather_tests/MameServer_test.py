# pylint: disable=E1101

import pytest
from cps2zmq.gather import MameServer

port = 6668
front_addr = ':'.join(["tcp://127.0.0.1", str(port)])
back_addr = ':'.join(["tcp://127.0.0.1", str(port + 1)])

worker_idn = bytes(str(1), encoding='UTF-8')
empty = b''
service = b'mame'

@pytest.fixture(scope="function")
def server():
    server = MameServer(front_addr, back_addr)
    yield server
    server.shutdown()

def test_setup(server):
    server.setup()
    assert server.msgreport is not None

def test_shutdown(server):
    server.shutdown()
    assert server.msgreport is None
