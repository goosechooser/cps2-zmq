import time
import pytest
import pymongo
from cps2_zmq.gather.MameServer import MameServer
from cps2_zmq.gather.MameWorker import MameWorker
from cps2_zmq.gather.DBSink import DBSink

# This is very finnicky
# Popping workers after they're done means you can't access any stats they collected
# @pytest.mark.timeout(timeout=10, method='thread')
def test_pipeline(client):
    server = MameServer(5666, "inproc://toworkers")
    workers = [MameWorker(str(num), "inproc://toworkers", "inproc://sink") for num in range(4)]
    server.workers = workers
    db_name = 'integration_test'
    sinks = [DBSink(str(1), "inproc://sink", db_name)]
    server.sinks = sinks

    client.start()
    server.start()

    # love too test nonblocking code
    time.sleep(10)

    server.cleanup()

    assert server.msgs_recv == sinks[0].msgs_recv

    db_client = pymongo.MongoClient()
    db = db_client[db_name]

    assert sinks[0].msgs_recv == db.frames.count()
    
    db.frames.drop()
    client.close()
