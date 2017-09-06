import os
import os.path
import pytest

def get_file(fpath):
    with open(os.path.normpath(fpath), 'r+b') as f:
        return f.read()

@pytest.fixture(scope='module') 
def rawframes():
    data_dir = os.path.normpath('tests/test_data/raw_frame_data/')
    frames = [get_file(os.path.join(data_dir, f)) for f in sorted(os.listdir(data_dir))]
    return frames