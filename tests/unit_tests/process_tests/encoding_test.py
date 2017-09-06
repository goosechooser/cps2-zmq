import json
import os
import pytest
from cps2zmq.process import encoding, Tile, Frame, Sprite

def is_json(str_):
    """
    If the string can be loaded without throwing an exception, its JSON.
    """
    try:
        json.loads(str_)
    except ValueError:
        return False
    return True

def test_frame_decode():
    framefile = 'tests/test_data/frame_1499.json'
    with open(os.path.normpath(framefile), 'r') as f:
        data = f.read()

    frame_decode = json.loads(data, cls=encoding.Cps2Decoder)
    assert isinstance(frame_decode, Frame)

def test_frame_encode(testframe):
    frame_encode = json.dumps(testframe, cls=encoding.Cps2Encoder)
    assert is_json(frame_encode)

def test_sprite_encode(testframe):
    sprite = testframe.sprites[0]
    sprite_encode = json.dumps(sprite, cls=encoding.Cps2Encoder)
    assert is_json(sprite_encode)

def test_sprite_decode():
    sprite_encode = '{"__module__": "cps2zmq.process.Sprite", "__class__": "Sprite",\
    "flips": [1, 0], \
    "tiles": [{"__type__": "tile", "dimensions": 16, "address":\
    "0x2f775", "data": null}], "base_tile": "0x2f775", "palnum": "0",\
    "location": [368, 208], "priority": 1, "size": [1, 1]}'

    sprite_decode = json.loads(sprite_encode, cls=encoding.Cps2Decoder)

    assert isinstance(sprite_decode, Sprite)

def test_tile_encode(testframe):
    tile = testframe.sprites[0].tiles[0]
    tile_encode = json.dumps(tile, cls=encoding.Cps2Encoder)

    assert is_json(tile_encode)

def test_tile_decode():
    tile_encode = '{"__class__": "Tile", "data": null,\
    "__module__": "cps2zmq.process.Tile", "dimensions": 16, "address": "0x2f775"}'
    tile_decode = json.loads(tile_encode, cls=encoding.Cps2Decoder)

    assert isinstance(tile_decode, Tile)
