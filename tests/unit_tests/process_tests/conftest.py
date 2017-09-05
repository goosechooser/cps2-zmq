import os
import mmap
import pytest
import json
# from cps2_zmq.process import encoding
from cps2_zmq.process import Frame

def get_file(fpath):
    return open(os.path.normpath(fpath), 'r+b')

def get_frame(framefile):
    with open(os.path.normpath(framefile), 'r') as f:
        data = f.read()
    return Frame.from_json(data)

@pytest.fixture(scope='module')
def testframe():
    return get_frame('tests/test_data/frame_1499.json')

@pytest.fixture(scope='module')
def gfxfile():
    return get_file('data/vm3_combined')

@pytest.fixture(scope='module')
def gfxmap():
    gfx = get_file('data/vm3_combined')
    return mmap.mmap(gfx.fileno(), 0)


