"""
Unit tests for MameWorker.py
"""
import pytest
from cps2_zmq.gather import MameWorker

@pytest.fixture(scope="function")
def test_worker():
    worker = MameWorker.MameWorker("1", "inproc://toworkers")
    yield worker
    worker.cleanup()

def test_sprite_mask():
    data = [420, 69, 300, 0]
    expected = {'tile_number': '0x012c',
                'priority': 0, 'xflip': 0, 'x': 420,
                'y': 69, 'eol': 0, 'yflip': 0,
                'height': 1, 'offset': 0, 'width': 1, 'pal_number': '0'}
    assert MameWorker.sprite_mask(data) == expected

# Get actual data to test with
# Ignores any list with a 0 in it, is that supposed to happen?
def test_mask_all():
    data = [[420, 69, 300, 1], [1, 1, 1, 1]]
    result1 = {'tile_number': '0x012c',
               'priority': 0, 'xflip': 0, 'x': 420,
               'y': 69, 'eol': 0, 'yflip': 0,
               'height': 1, 'offset': 0, 'width': 1, 'pal_number': '1'}

    result2 = {'tile_number': '0x01',
               'priority': 0, 'xflip': 0, 'x': 1,
               'y': 1, 'eol': 0, 'yflip': 0,
               'height': 1, 'offset': 0, 'width': 1, 'pal_number': '1'}

    expected = [result1, result2]
    results = MameWorker.mask_all(data)

    for i, r in enumerate(results):
        assert r == expected[i]

@pytest.mark.parametrize("message, expected", [
    ({'frame_number': 1141, 'sprites': [[420, 69, 300, 1], [1, 1, 1, 1]], 'palettes': [[]]}, 1141),
])
def test_process_message(message, expected):
    result = MameWorker._process_message(message)
    print(result)
    assert result[0] == expected

@pytest.mark.parametrize("message, expected", [
    ({'frame_number': 0, 'sprites': [], 'palettes': []}, 0),
    ({'frame_number': 'closing', 'sprites': [], 'palettes': []}, 'closing'),
])
def test_work(message, expected):
    """
    Not sure this test/method is useful anymore.
    If I can figure out the root cause of why json errors
    were being thrown in the first place, I can get rid of them.
    """
    result = MameWorker._work(message)
    assert result == expected

@pytest.mark.timeout(timeout=10, method='thread')
@pytest.mark.parametrize("messages, expected", [
    (1, 1),
    (10, 10)
])
def test_run(server, test_worker, messages, expected):
    # worker = MameWorker.MameWorker("1", "inproc://toworkers")
    test_worker.start()
    print("Worker started")
    server.make_messages(messages)
    print("Messages made")
    server.start()
    assert test_worker.msgs_recv == expected
