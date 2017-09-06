# pylint: disable=E1101

import pytest
from cps2zmq.gather import BaseSink
from cps2zmq.gather import mdp

idn = 'sink-1'
port = 6666
addr = ':'.join(["tcp://127.0.0.1", str(port)])
sub_addr = ':'.join(["tcp://127.0.0.1", str(port + 1)])

empty = b''

@pytest.fixture(scope='function')
def sink():
    s = BaseSink(idn, addr, sub_addr, "mongodb")
    yield s
    s.close()

def test_setup(sink):
    assert sink.substream != None

def test_close(sink):
    sink.close()
    assert sink.substream == None
