import pytest
from cps2_zmq.gather.MameServer import MameServer
from cps2_zmq.gather.MameSink import MameSink
from cps2_zmq.gather.MameWorker import MameWorker

@pytest.mark.skip()
@pytest.mark.timeout(timeout=10, method='thread')
def test_pipeline(server):
    num_workers = 2

    server = MameServer(5556, "inproc://toworkers")
    workers = [MameWorker("inproc://toworkers", "inproc://fromworkers", "inproc://control")
               for i in range(num_workers)]
    sink = MameSink("inproc://fromworkers", "inproc://control")
    sink.workers = workers
    server.worksink = sink
    server.msg_limit = None
    server.run()
    server.start()
    print(server.msgs_recv)
    assert 0