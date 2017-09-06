import json
import pytest
import msgpack
import pymongo
from cps2zmq.gather import MongoSink
from cps2zmq.gather import mdp

idn = 'sink-1'
port = 6666
addr = ':'.join(["tcp://127.0.0.1", str(port)])
sub_addr = ':'.join(["tcp://127.0.0.1", str(port + 1)])
db_name = 'sink_test'

@pytest.fixture(scope='function')
def sink():
    s = MongoSink(idn, addr, sub_addr, "mongodb", db_name)
    yield s
    s.close()

@pytest.fixture(scope='function')
def db():
    client = pymongo.MongoClient()
    db = client[db_name]
    yield db
    client.drop_database(db_name)
    client.close()

@pytest.mark.skip
def test_process_pub(sink, db):
    message = json.dumps({'test': 'message'})
    sink.process_pub(msgpack.packb(message))

    assert db[sink.topics].find_one()
