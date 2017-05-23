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

@pytest.mark.parametrize("message, expected",[
    (0, 0),
    (1141, 1141),
    ('closing', 'closing'),
])
def test_process_message(message, expected):
    test_message = {'frame_number': message, 'sprites': [], 'palettes': []}
    result = MameWorker._process_message(test_message)
    assert result == expected

@pytest.mark.parametrize("message, expected",[
    ({'frame_number': 0, 'sprites': [], 'palettes': []}, {}),
    ({'frame_number': 1141, 'sprites': [[420, 69, 300, 1]], 'palettes': [[]]}, 1141),
    ({'frame_number': 'closing', 'sprites': [], 'palettes': []}, 'closing'),
])
def test_work(message, expected):
    result = MameWorker._work(message)
    assert result == expected
