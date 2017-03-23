import jsonpickle
from PIL import Image

class Frame(object):
    """
    Frame is a container of Sprites.
    """
    def __init__(self, fnumber, sprites, palettes):
        """
        Construct a new 'Frame' object.
        In most cases you want to use the factory methods

        Args:
            fnumber (int): the frame number
            palettes (dict): the 32 x 16 colors of Frame
            sprites ([Sprite]): the Sprites of Frame
        """
        self._fnumber = fnumber
        self._palettes = palettes
        self._sprites = sprites

    def __repr__(self):
        return "Frame {} has {} sprites".format(self._fnumber, len(self._sprites))

    @property
    def fnumber(self):
        """
        Get fnumber
        """
        return self._fnumber

    @property
    def sprites(self):
        """
        Get sprites
        """
        return self._sprites

    @property
    def palettes(self):
        """
        Get palettes
        """
        return self._palettes

    def add_sprites(self, sprites):
        """
        Add sprites to the Frame's existing sprites.

        Args:
            sprites ([Sprite]): a list of sprites
        """
        self._sprites.extend(sprites)

    # Only needs to create a png, doesn't need to color in sprites
    # Issues arise from assuming all the sprites are already colored
    # Uncolored tiles are output by using 'P'(palette) mode
    def topng(self, fname, imsize=(400, 400)):
        """
        Saves the Frame as a PNG file.

        Args:
            fname (str): the name to save the PNG file as.
            imsize ((int, int)): The size of the PNG file. A tuple.
        """
        canvas = Image.new('RGB', imsize)
        for sprite in self._sprites:
            canvas.paste(
                Image.fromarray(sprite.toarray(), 'RGB'),
                sprite.location
                )
        canvas.save('.'.join([fname, 'png']))

    def tofile(self, path):
        """
        Saves the Frame object as a json encoded file.

        Args:
            path (str): The location to save to.
        """
        file_name = '.'.join([str(self._fnumber), 'json'])
        path = '\\'.join([path, file_name])

        with open(path, 'w') as f:
            f.write(jsonpickle.encode(self))

# Factories
def new(fnumber, sprites, palettes):
    """
    A factory method for Frame. Converts the palettes given into tuples.

    Args:
        fnumber (int): the frame number
        sprites ([Sprite]): a list of Sprites
        palettes (dict): a dict of 32 keys. Each key is paired with another dict of length 16.

    Returns:
        a Frame object
    """
    converted = {}
    for k, v in palettes.items():
        conv = {kk : _argb_to_rgb(hex(color)[2:]) for kk, color in v.items()}
        converted[k] = conv

    return Frame(fnumber, sprites, converted)

def fromfile(path):
    """
    Returns a Frame from a json encoded file.

    Args:
        path (str): path to the json file.

    Returns:
        a Frame object
    """
    with open(path, 'r') as f:
        frame = jsonpickle.decode(f.read())

    return frame

def _argb_to_rgb(color):
    """
    Converts the 2 byte ARGB format the cps2 uses to a tuple of RGB values.

    Args:
        color (bytes): a 2 byte value in ARGB format

    Returns:
        a tuple of 3 ints (R, G, B)
    """
    if len(color) < 4:
        color = (4 - len(color)) * '0' + color

    return (int(color[1] * 2, 16), int(color[2] * 2, 16), int(color[3] * 2, 16))

# One day
def from_image(image, frame):
    pass
