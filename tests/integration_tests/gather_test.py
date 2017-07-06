import pytest
from cps2_zmq.gather.MameServer import MameServer
from cps2_zmq.gather.MameWorker import MameWorker

# This is very finnicky
# Popping workers after they're done means you can't access any stats they collected
@pytest.mark.timeout(timeout=10, method='thread')
def test_pipeline(client):
    server = MameServer(5666, "inproc://toworkers")
    workers = [MameWorker(str(num), "inproc://toworkers", "inproc://none") for num in range(1, 3)]
    server.workers = workers
    client.msgs = client.msgs
    client.start()
    server.start()
    server.cleanup()

    # This aint a great test for a PUB/SUB pattern since its likely messages would get lost
    assert server.msgs_recv == len(client.msgs)
    