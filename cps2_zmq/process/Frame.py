# import jsonpickle
import json
from PIL import Image
# from cps2_zmq.process import encoding
from cps2_zmq.process.GraphicAsset import GraphicAsset

class Frame(GraphicAsset):
    """
    Frame is a container of Sprites. It is related to the frames drawn by the CPS2 hardware.
    Ideally this would provide methods for manipulating sprites en masse.

    Attributes:
        fnumber (int): the frame number.\
        Frames should have a unique fnumber (linearly increasing).
        sprites (:obj:`list` of :obj:`Sprite.Sprite`): the Sprites of the Frame
        palettes (dict): contains the 32 palettes used by Sprites/ColorTiles in the Frame
    """
    def __init__(self, fnumber, sprites, palettes):
        """
        Construct a new 'Frame' object. In most cases you want to use the factory methods
        """
        self.fnumber = fnumber
        self.sprites = sprites
        self.palettes = palettes

    def __repr__(self):
        return "Frame {} has {} sprites".format(self.fnumber, len(self.sprites))

    def add_sprites(self, sprites):
        """
        Add sprites to the Frame's existing sprites.

        Args:
            sprites (:obj:`list` of :obj:`Sprite.Sprite`): a list of sprites
        """
        self.sprites.extend(sprites)
    def to_array(self):
        pass

    # Only needs to create a png, doesn't need to color in sprites
    # Issues arise from assuming all the sprites are already colored
    # Uncolored tiles are output by using 'P'(palette) mode
    def to_png(self, fname, imsize=(400, 400)):
        """
        Saves the Frame as a PNG file.

        Args:
            fname (str): the name to save the PNG file as.
            imsize (int, int, optional): The size of the PNG file. Defaults to (400, 400)
        """
        canvas = Image.new('RGB', imsize)
        for sprite in self.sprites:
            canvas.paste(
                Image.fromarray(sprite.to_array(), 'RGB'),
                sprite.location
                )
        canvas.save('.'.join([fname, 'png']))

    def to_file(self, path):
        """
        Saves the Frame object as a json encoded file.

        Args:
            path (str): The location to save to.
        """
        name = '_'.join(['frame', str(self.fnumber)])
        file_name = '.'.join([name, 'json'])
        path = '\\'.join([path, file_name])

        with open(path, 'w') as f:
            f.write(self.to_json())

# Factories
def new(fnumber, sprites, palettes):
    """
    A factory method for Frame. Converts the palettes given into tuples.

    Args:
        fnumber (int): the frame number
        sprites (:obj:`list` of :obj:`Sprite.Sprite`): a list of Sprites
        palettes (dict): a dict of 32 keys. Each key is paired with another dict of length 16.

    Returns:
        a Frame object
    """
    converted = {}
    for k, v in palettes.items():
        # conv = {kk : _argb_to_rgb(hex(color)[2:]) for kk, color in v.items()}
        conv = [_argb_to_rgb(hex(color)[2:]) for color in v]
        converted[k] = conv

    return Frame(fnumber, sprites, converted)

def from_file(path):
    """
    Returns a Frame from a json encoded file.

    Args:
        path (str): path to the json file.

    Returns:
        a Frame object
    """
    with open(path, 'r') as f:
        frame = json.dumps(f.read())

    return frame

def _argb_to_rgb(color):
    """
    Converts the 2 byte ARGB format the cps2 uses to a tuple of RGB values.

    Args:
        color (bytes): a 2 byte value in ARGB format.

    Returns:
        an (int, int, int) representing the RGB value of a pixel.
    """
    if len(color) < 4:
        color = (4 - len(color)) * '0' + color

    return (int(color[1] * 2, 16), int(color[2] * 2, 16), int(color[3] * 2, 16))

def from_image(image, frame):
    """
    Unimplemented. One day.
    """
    pass
