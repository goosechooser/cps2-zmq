import pytest
import msgpack
from cps2_zmq.gather import DBWorker, MameWorker

def test_process_message(rawframes):
    dbworker = DBWorker.DBWorker("1", "inproc://fordb", 'cps2_test')
    packed = rawframes[0]

    raw = msgpack.unpackb(packed, encoding='UTF-8')
    raw_frame = MameWorker.process_message(raw)
    # packed = msgpackk.packb(raw_frame.to_json())

    dbworker.process(raw_frame.to_json())
    dbworker.close()

    assert dbworker.db.frames.count() == 1
    