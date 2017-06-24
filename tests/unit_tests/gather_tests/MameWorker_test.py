"""
Unit tests for MameWorker.py
"""
import pytest
from cps2_zmq.gather import MameWorker

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
    result = MameWorker._work(message)
    assert result == expected

@pytest.mark.parametrize("messages, expected", [
    ([{'frame_number': 1141, 'sprites': [[420, 69, 300, 1], [1, 1, 1, 1]], 'palettes': [[]]},
      {'frame_number': 0, 'sprites': [], 'palettes': []}], 1)
])
# @pytest.mark.timeout(timeout=10, method='thread')
def test_run(server, sink, messages, expected):
    worker = MameWorker.MameWorker("inproc://toworkers",
                                   "inproc://mockworkers",
                                   "inproc://mockcontrol")
    worker.daemon = True
    worker.start()
    server.push_messages(messages)
    sink.msg_limit = expected
    results = sink.run()
    assert len(results) == expected
