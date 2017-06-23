import pytest
from cps2_zmq.gather.MameClient import MameClient

def test_worksink(sink):
    client = MameClient(666, "inproc://yas")
    client.worksink = sink

    assert client.worksink == sink

    with pytest.raises(TypeError) as e:
        client.worksink = "fail"
    client.cleanup()
    
@pytest.mark.parametrize("message, expected", [
    ({'frame_number' : 10}, True),
    ({'frame_number' : 'closing'}, False),
])
def test_process_message(message, expected):
    client = MameClient(666, "inproc://yas")
    client.process_message(message)
    assert client._working == expected
    client.cleanup()
