# pylint: disable=E0202
"""
For serializing our objects.
For deserializing our objects - soon.
"""
import importlib
import json
from cps2_zmq.process import Frame, Sprite, Tile

class Cps2Decoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_obj)

    def dict_to_obj(self, d):
        if '__type__' not in d:
            return d

        type_ = d.pop('__type__')
        if type_ == 'tile':
            module = importlib.import_module('cps2_zmq.process.Tile')
            class_ = getattr(module, 'Tile')
            args = dict((key, value) for key, value in d.items())
            return class_(**args)

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
            dict_ = dict((k, v) for k, v in o.__dict__.items())
            dict_['_sprites'] = [handle_sprite_dict(s) for s in dict_['_sprites']]
            dict_['__type__'] = 'frame'
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
    tile = dict((k, v) for k, v in obj.__dict__.items())
    tile['__type__'] = 'tile'
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
    sprite['__type__'] = 'sprite'

    return sprite
    