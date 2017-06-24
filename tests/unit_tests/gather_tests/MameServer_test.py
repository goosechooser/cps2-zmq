import pytest
from cps2_zmq.gather.MameServer import MameServer

def test_worksink(sink):
    server = MameServer(666, "inproc://yas")
    server.worksink = sink

    assert server.worksink == sink

    with pytest.raises(TypeError) as e:
        server.worksink = "fail"
    server.cleanup()

@pytest.mark.timeout(timeout=10, method='thread')
def test_start(client, worker):
    client.msg_limit = 100

    server = MameServer(5666, "inproc://tomockworkers")
    client.start()
    server.start()

    worker.pull_messages()

    assert server.msgs_recv == worker.msgs_recv

# @pytest.mark.parametrize("message, expected", [
#     ({'frame_number' : 10}, True),
#     ({'frame_number' : 'closing'}, False),
# ])
# def test_process_message(message, expected):
#     server = MameServer(666, "inproc://yas")
#     server.process_message(message)
#     assert server._stream.closed == expected
#     server.cleanup()


