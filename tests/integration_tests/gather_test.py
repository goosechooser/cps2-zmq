import time
import pytest
import pymongo
from cps2_zmq.gather import MameServer
from cps2_zmq.gather import MameWorker

# db_name = 'integration_test'

# @pytest.fixture(scope="module")
# def db():
#     db_client = pymongo.MongoClient()
#     db = db_client[db_name]
#     yield db
#     db_client.drop_database(db_name)
#     db_client.close()

# @pytest.mark.skip
@pytest.mark.timeout(timeout=20, method='thread')
def test_pipeline(client):
    server = MameServer("tcp://127.0.0.1:5666", "tcp://127.0.0.1:5557")
    workers = [MameWorker(str(num), "tcp://127.0.0.1:5557", b'mame') for num in range(2)]

    client.start()
    server.start()

    # love too test nonblocking code
    time.sleep(5)
    server.shutdown()

    assert server.frontstream == None
    assert server.backstream == None

    msgs_sum = 0
    for w in workers:
        w.close()
        msgs_sum += w.msgs_recv
        assert w.heartbeater == None
        assert w.frontstream == None

    assert server.msgs_recv == msgs_sum
