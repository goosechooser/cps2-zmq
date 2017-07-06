import pytest
import msgpack
from cps2_zmq.gather import DBSink, MameWorker

def test_process_message(rawframes):
    sink = DBSink.DBSink("1", "inproc://fordb", 'cps2_test')
    packed = rawframes[0]
    
    sink.db.frames.drop()
    
    raw = msgpack.unpackb(packed, encoding='UTF-8')
    raw_frame = MameWorker.process_message(raw)

    sink.process(raw_frame.to_json())
    sink.close()

    assert sink.db.frames.count() == 1
    