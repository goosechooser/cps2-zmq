import mmap
import pytest
import jsonpickle

def get_file(fpath):
    return open(fpath, 'r+b')

def get_frame(framefile):
    with open(framefile, 'r') as f:
        data = f.read()
    return jsonpickle.decode(data)

FRAME = get_frame('frame_data\\1141.json')
GFXFILE = get_file('data\\vm3_combined')
GFXMAP = mmap.mmap(GFXFILE.fileno(), 0)

@pytest.fixture(scope='module')
def testframe():
    return get_frame('frame_data\\1141.json')

@pytest.fixture(scope='module')
def gfxfile():
    return get_file('data\\vm3_combined')

@pytest.fixture(scope='module')
def gfxmap():
    gfxfile = get_file('data\\vm3_combined')
    return mmap.mmap(gfxfile.fileno(), 0)


