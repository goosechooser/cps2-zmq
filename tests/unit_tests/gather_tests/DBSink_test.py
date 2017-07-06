import pytest
import msgpack
import pymongo
from cps2_zmq.gather import DBSink, MameWorker

db_name = 'cps2_test'

@pytest.fixture(scope="module")
def db():
    db_client = pymongo.MongoClient()
    db = db_client[db_name]
    yield db
    db_client.drop_database(db_name)
    db_client.close()

def test_process_message(rawframes, db):
    sink = DBSink.DBSink("1", "inproc://fordb", db_name)
    packed = rawframes[0]
    
    raw = msgpack.unpackb(packed, encoding='UTF-8')
    raw_frame = MameWorker.process_message(raw)

    sink.process(raw_frame.to_json())
    sink.close()

    assert db.frames.count() == 1
    