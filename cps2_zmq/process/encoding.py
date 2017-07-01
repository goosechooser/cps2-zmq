# pylint: disable=E0202
"""
For serializing our objects.
For deserializing our objects - soon.
"""
import importlib
import json
import cps2_zmq.process
# import cps2_zmq.process.Frame
# from cps2_zmq.process.Sprite import Sprite
# from cps2_zmq.process.Tile import Tile

class Cps2Decoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_obj)

    def dict_to_obj(self, d):
        """
        Decodes a JSON object into the appropiate python object.

        Args:
            d (str): a string representing a JSON object

        Returns:
            a python object. Currently supports Frame, Sprite, and Tile objects.\
            Returns d otherwise.
        """
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            args = d
            return class_(**args)

        else:
            return d

class Cps2Encoder(json.JSONEncoder):
    """
    For serializing Frame, Sprite, and Tile objects.
    """
    def default(self, o):
        if isinstance(o, cps2_zmq.process.Tile.Tile):
            return handle_tile_dict(o)

        if isinstance(o, cps2_zmq.process.Sprite.Sprite):
            return handle_sprite_dict(o)

        if isinstance(o, cps2_zmq.process.Frame.Frame):
            dict_ = dict((k, v) for k, v in o.__dict__.items())
            dict_['sprites'] = [handle_sprite_dict(s) for s in dict_['sprites']]
            insert_module_class(dict_, o)

            return dict_

        return json.JSONEncoder.default(self, o)

def handle_tile_dict(obj):
    """
    Massages a Tile into a dict for serializing.

    Args:
        obj (Tile): a Tile

    Returns:
        a dict.
    """
    tile = dict((k, v) for k, v in obj.__dict__.items())
    tile = insert_module_class(tile, obj)
    return tile

def handle_sprite_dict(obj):
    """
    Massages a Sprite into a dict for serializing.

    Args:
        obj (Sprite): a Sprite

    Returns:
        a dict.
    """
    sprite = dict([(k, v) for k, v in obj.__dict__.items() if k != 'tiles'])
    sprite['tiles'] = [handle_tile_dict(tile) for tile in obj.tiles]
    sprite = insert_module_class(sprite, obj)

    return sprite

def insert_module_class(d, obj):
    """
    Inserts the class name and module name into a dict.
    """
    d['__class__'] = obj.__class__.__name__
    d['__module__'] = obj.__module__

    return d
    