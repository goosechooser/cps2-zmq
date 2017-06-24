import pytest
from cps2_zmq.gather.MameServer import MameServer

def test_worksink(sink):
    server = MameServer(666, "inproc://yas")
    server.worksink = sink

    assert server.worksink == sink

    with pytest.raises(TypeError) as e:
        server.worksink = "fail"
    server.cleanup()
    
@pytest.mark.parametrize("message, expected", [
    ({'frame_number' : 10}, True),
    ({'frame_number' : 'closing'}, False),
])
def test_process_message(message, expected):
    server = MameServer(666, "inproc://yas")
    server.process_message(message)
    assert server._working == expected
    server.cleanup()
