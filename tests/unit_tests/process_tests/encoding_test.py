import json
import pytest
from cps2_zmq.process import encoding, Tile

def is_json(str_):
    try:
        json_object = json.loads(str_)
    except ValueError:
        return False
    return True

def test_frame_encode(testframe):
    frame_encode = json.dumps(testframe, cls=encoding.Cps2Encoder)
    assert is_json(frame_encode)

def test_sprite_encode(testframe):
    sprite = testframe.sprites[0]
    sprite_encode = json.dumps(sprite, cls=encoding.Cps2Encoder)
    assert is_json(sprite_encode)

def test_tile_encode(testframe):
    tile = testframe.sprites[0].tiles[0]
    tile_encode = json.dumps(tile, cls=encoding.Cps2Encoder)
    assert is_json(tile_encode)

    tile_decode = json.loads(tile_encode, cls=encoding.Cps2Decoder)
    print(tile_decode)

    assert isinstance(tile_decode, Tile.Tile)
    