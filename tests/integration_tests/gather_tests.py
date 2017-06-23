from cps2_zmq.gather.MameClient import MameClient
from cps2_zmq.gather.MameSink import MameSink
from cps2_zmq.gather.MameWorker import MameWorker

def test_pipeline(server):
    num_workers = 2

    client = MameClient(5556, "inproc://toworkers")
    workers = [MameWorker("inproc://toworkers", "inproc://fromworkers", "inproc://control")
               for i in range(num_workers)]
    sink = MameSink("inproc://fromworkers", "inproc://control")
    sink.workers = workers
    client.worksink = sink
    client.start()
