# pylint: disable=E1101

import pytest
from cps2_zmq.gather.BaseSink import BaseSink
from cps2_zmq.gather import mdp

idn = 'sink-1'
port = 6666
addr = ':'.join(["tcp://127.0.0.1", str(port)])
sub_addr = ':'.join(["tcp://127.0.0.1", str(port + 1)])

empty = b''
service = b'logging'

@pytest.fixture(scope='function')
def sink():
    s = BaseSink(idn, addr, service, sub_addr, "mongodb")
    yield s
    s.close()

def test_setup(sink):
    assert sink.substream != None

def test_close(sink):
    sink.close()
    assert sink.substream == None

def test_handle_message(sink):
    test_msg = [empty, sink._protocol, mdp.READY]
    with pytest.raises(mdp.UnsupportedCommandException):
        sink.handle_message(test_msg)
