import pytest
from cps2_zmq.gather.MameServer import MameServer

@pytest.mark.skip
@pytest.mark.timeout(timeout=10, method='thread')
def test_start(client, worker):
    client.msg_limit = 100

    server = MameServer(5666, "inproc://tomockworkers")
    client.start()
    server.start()

    worker.pull_messages()

    assert server.msgs_recv == worker.msgs_recv



