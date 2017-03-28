import os
import mmap
import pytest
import jsonpickle

def get_file(fpath):
    return open(fpath, 'r+b')

def get_frame(framefile):
    with open(framefile, 'r') as f:
        data = f.read()
    return jsonpickle.decode(data)

@pytest.fixture(scope='module')
def testframe():
    return get_frame('frame_data\\frame_1526.json')

@pytest.fixture(scope='module')
def testframes():
    return iter([get_frame('\\'.join(['frame_data_2', f])) for f in os.listdir('frame_data\\')])

@pytest.fixture(scope='module')
def gfxfile():
    return get_file('data\\vm3_combined')

@pytest.fixture(scope='module')
def gfxmap():
    gfx = get_file('data\\vm3_combined')
    return mmap.mmap(gfx.fileno(), 0)


