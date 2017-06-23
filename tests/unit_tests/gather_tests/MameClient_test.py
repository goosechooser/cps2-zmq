import pytest
from cps2_zmq.gather.MameClient import MameClient

def test_worksink(sink):
    client = MameClient(666)
    client.worksink = sink
    
    assert client.worksink == sink

    with pytest.raises(TypeError) as e:
        client.worksink = "fail"
