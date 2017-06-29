import json
import pytest
from cps2_zmq.process import encoding

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
    