# pylint: disable=E0202
"""
For serializing our objects.
For deserializing our objects - soon.
"""
import json
from cps2_zmq.process import Frame, Sprite, Tile

class Cps2Encoder(json.JSONEncoder):
    """
    For serializing Frame, Sprite, and Tile objects.
    """
    def default(self, o):
        if isinstance(o, Tile.Tile):
            return handle_tile_dict(o)

        if isinstance(o, Sprite.Sprite):
            return handle_sprite_dict(o)

        if isinstance(o, Frame.Frame):
            dict_ = o.__dict__
            dict_['_sprites'] = [handle_sprite_dict(s) for s in dict_['_sprites']]
            dict_['__type__'] = 'Frame'
            return dict_

        return json.JSONEncoder.default(self, o)

def handle_tile_dict(obj):
    """
    Massages a Tile into a dict for serializing.

    Args:
        obj ()

    Returns:
        a dict.
    """
    tile = obj.__dict__
    tile['__type__'] = 'Tile'
    return tile

def handle_sprite_dict(obj):
    """
    Massages a Sprite into a dict for serializing.

    Args:
        obj ()

    Returns:
        a dict.
    """
    sprite = dict([(k, v) for k, v in obj.__dict__.items() if k != '_tiles'])
    sprite['_tiles'] = [handle_tile_dict(tile) for tile in obj.tiles]
    sprite['__type__'] = 'Sprite'

    return sprite
    