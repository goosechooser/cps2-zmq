from cps2_zmq.gather import MameWorker
from cps2_zmq.process import Sprite

def test_sprite_mask():
    data = [420, 69, 300, 0]
    expected = {'tile_number': '0x012c',
                'priority': 0, 'xflip': 0, 'x': 420,
                'y': 69, 'eol': 0, 'yflip': 0,
                'height': 1, 'offset': 0, 'width': 1, 'pal_number': '0'}
    assert MameWorker.sprite_mask(data) == expected

def test_work():
    empty_message = {'frame_number': 0, 'sprites': [], 'palettes': []}
    result = MameWorker._work(empty_message)
    assert result == {}

    # data = [420, 69, 300, 0]
    # partial_message = {'frame_number': 1141, 'sprites': [data], 'palettes': [[]]}

    # expected = {'tile_number': '0x012c',
    #             'priority': 0, 'xflip': 0, 'x': 420,
    #             'y': 69, 'eol': 0, 'yflip': 0,
    #             'height': 1, 'offset': 0, 'width': 1, 'pal_number': '0'}

    # message, sprite, palettes = MameWorker._work(partial_message)
    # assert sprites == expected

