import os
import mmap
import pytest
import json
from cps2_zmq.process import encoding

def get_file(fpath):
    return open(os.path.normpath(fpath), 'r+b')

def get_frame(framefile):
    with open(os.path.normpath(framefile), 'r') as f:
        data = f.read()
    return json.loads(data, cls=encoding.Cps2Decoder)

@pytest.fixture(scope='module')
def testframe():
    return get_frame('tests/test_data/frame_1499.json')

@pytest.fixture(scope='module')
def testframes():
    return iter([get_frame('\\'.join(['frame_data_2', f])) for f in os.listdir('frame_data\\')])

@pytest.fixture(scope='module')
def gfxfile():
    return get_file('data/vm3_combined')

@pytest.fixture(scope='module')
def gfxmap():
    gfx = get_file('data/vm3_combined')
    return mmap.mmap(gfx.fileno(), 0)


