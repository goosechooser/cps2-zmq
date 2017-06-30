import jsonpickle
from PIL import Image
import numpy as np

from cps2_zmq.process import Tile, ColorTile

class Sprite(object):
    """
    A Sprite encapsulates a collection of :py:mod:`~cps2_zmq.gather.Tile.Tile` that use the same palette.

    Attributes:
        base_tile (str): the address in memory of the first :py:mod:`~cps2_zmq.gather.Tile.Tile` in the grouping
        tiles (:obj:`list` of :py:mod:`~cps2_zmq.gather.Tile.Tile`): a list of Tiles that make up the Sprite
        palnum (int): which of the 32 palettes in a Frame the Sprite uses
        location (int, int): the (x,y) coordinate where the Sprite will be drawn on the screen
        size (int, int): (width, height) the size of the Sprite in Tiles.
            (1, 1) means a single Tile.
        flips (int, int): (xflip, yflip) determines whether the Sprite needs to be flipped over its X or Y axis.
        priority (int): determines what other Sprites will be covered or which Sprites will cover this Sprite.
            0 is lowest, 3 is highest.
    """
    def __init__(self, base_tile, tiles, palnum, location, size, flips, priority=0):
        self.base_tile = base_tile
        self.tiles = tiles
        self.palnum = palnum
        self.location = location
        self.size = size
        self.flips = flips
        self.priority = priority

    def __repr__(self):
        addrs = [tile.address for tile in self.tiles if tile]
        loc = " Location: (" + str(self.location[0]) + ", " + str(self.location[1])
        size = " Size: (" + str(self.size[0]) + ", " + str(self.size[1])
        return "Sprite contains tiles: " + str(addrs) + loc + ")" + size + ")"



    def height(self):
        return self.size[1]

    def width(self):
        return self.size[0]

    def to_array(self, flip=True):
        """
        Provides contents of Sprite as a numpy array.
        Does any necessary flips in the process.

        Args:
            flip (bool, optional): Whether or not the Sprite contents are flipped. Defaults to True.

        Returns:
            a 2D numpy array.
        """

        arrays = [tile.to_array() for tile in self.tiles]
        array2d = list2d(arrays, self.size)
        array_rows = [np.concatenate(row, axis=1) for row in array2d]
        preflip = np.concatenate(array_rows, axis=0)

        if flip and self.flips[0]:
            preflip = np.fliplr(preflip)
        if flip and self.flips[1]:
            preflip = np.flipud(preflip)

        return preflip

    def color_tiles(self, palette):
        """
        Converts any :obj:`Tile` the :obj:`Sprite` has into :obj:`ColorTile`.

        Args:
            palette (dict): the palette to use.
        """

        self.tiles = [ColorTile.from_tile(tile, palette)
                       for tile in self.tiles
                       if isinstance(tile, Tile.Tile)]

    def to_bmp(self, path_to_save):
        """
        Creates a .bmp file
        """
        try:
            image = Image.fromarray(self.to_array(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.to_array(), 'P')
        image.save(path_to_save + ".bmp")

    def to_png(self, path_to_save):
        """
        Creates a .png file
        """
        try:
            image = Image.fromarray(self.to_array(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.to_array(), 'P')
        image.save(path_to_save + ".png")

    def to_tile(self):
        """
        This method is *probably* used when writing the contents of the :obj:`Sprite` to file.
        Converts any :obj:`ColorTile` objects the :obj:`Sprite` has to :obj:`Tile` objects.

        Returns:
            a list of Tiles.
        """
        return [t.to_tile() if isinstance(t, ColorTile.ColorTile) else t for t in self.tiles]

    def to_file(self, path):
        """
        Saves the Sprite object as a json encoded file.

        Args:
            path (str): The location to save to.
        """
        name = '_'.join(['sprite', str(self.base_tile)])
        file_name = '.'.join([name, 'json'])
        path = '\\'.join([path, file_name])

        with open(path, 'w') as f:
            f.write(jsonpickle.encode(self))

# todo: exception handling for sizing issues
def list2d(list_, size):
    """
    Turns a linear :obj:`list` into a list of lists.

    Args:
        size (int, int): the desired size of the reshaped list

    Returns:
        a list of lists
    """
    list_2d = []
    for i in range(size[1]):
        offset = size[0] * i
        list_2d.append(list_[offset:offset + size[0]])
    return list_2d

# Factories
# todo: exception handling related to improperly formed dict
def from_dict(dict_):
    """
    A factory method to create a Sprite from a dict of params.

    Args:
        dict_ (dict): a dict of parameters.

    Returns:
        a Sprite. The Tiles in the Sprite are empty at this point though,
        and will need to be filled in. This can be done by calling
        `tile_operations.read_tiles_from_file`
    """
    palnum = dict_['pal_number']

    tile_number = dict_['tile_number']
    size = (dict_['width'], dict_['height'])
    loc = (dict_['x'], dict_['y'])
    flips = (dict_['xflip'], dict_['yflip'])
    if dict_['offset'] is 0:
        loc = (loc[0] - 64, loc[1] - 16)

    tiles = []
    for i in range(size[1]):
        for j in range(size[0]):
            offset = i * 0x10 + j * 0x1
            addr = hex(int(tile_number, 16) + offset)
            tiles.append(Tile.Tile(addr, None))

    return Sprite(tile_number, tiles, palnum, loc, size, flips, priority=dict_['priority'])

def from_file(path):
    """
    Returns a Sprite from a json encoded file.

    Args:
        path (str): path to the json file.

    Returns:
        a Sprite object
    """
    with open(path, 'r') as f:
        sprite = jsonpickle.decode(f.read())

    return sprite

def from_image(image, sprite):
    """
    Converts a image into a :obj:`Sprite`.

    Args:
        image (str): path to an image.\
        Currently only .bmp and .png images are known to work, others may or may not.
        sprite (:obj:`Sprite`): The attributes of the :obj:`Sprite`\
        will be used by the new :obj:`Sprite`.

    Returns:
        a Sprite.
    """
    im = Image.open(image)

    if sprite.flips[0]:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if sprite.flips[1]:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)

    cropped_imgs = []
    addresses = []
    for i in range(sprite.size[1]):
        for j in range(sprite.size[0]):
            change = (16 * j, 16 * i, 16 + 16 * j, 16 + 16 * i)
            cropped_imgs.append(im.crop(change))
            changed_addr = int(sprite.base_tile, 16) + 0x10 * i + 0x1 * j
            addresses.append(hex(changed_addr))

    zipped = zip(cropped_imgs, addresses)

    if im.mode == 'P':
        tiles = [Tile.new(addr, bytes(img.getdata())) for img, addr in zipped]

    if im.mode == 'RGB':
        tiles = [ColorTile.new(addr, list(img.getdata()), None) for img, addr in zipped]

    new_sprite = sprite
    new_sprite.tiles = tiles
    return new_sprite

def sprite_mask(byte_data):
    """
    Turns the 8 bytes of raw sprite information into something usable.

    Args:
        byte_data (:obj:`list`): a list of 4 uint16 containing all the data for a Sprite.

    Returns:
        a dict. This dict can be used by the Sprite factory method :meth:`fromdict`.
    """
    dict_ = {}
    dict_['priority'] = (byte_data[0] & 0xC000) >> 14
    dict_['x'] = byte_data[0] & 0x03FF
    dict_['y'] = byte_data[1] & 0x03FF
    dict_['eol'] = (byte_data[1] & 0x8000) >> 15
    #hex: {0:x};  oct: {0:o};  bin: {0:b}".format(42)
    top_half = "{0:#x}".format((byte_data[1] & 0x6000) >> 13)
    bottom_half = "{0:x}".format(byte_data[2])
    dict_['tile_number'] = ''.join([top_half, bottom_half])
    dict_['height'] = ((byte_data[3] & 0xF000) >> 12) + 1
    dict_['width'] = ((byte_data[3] & 0x0F00) >> 8) + 1
    #(0= Offset by X:-64,Y:-16, 1= No offset)
    dict_['offset'] = (byte_data[3] & 0x0080) >> 7
    #Y flip, X flip (1= enable, 0= disable)
    dict_['yflip'] = (byte_data[3] & 0x0040) >> 69
    dict_['xflip'] = (byte_data[3] & 0x0020) >> 5
    dict_['pal_number'] = "{0:d}".format(byte_data[3] & 0x001F)
    # dict_['mem_addr'] = "{0:x}".format(byte_data[4])

    return dict_

def mask_all(sprites):
    """
    Calls sprite_mask on every value in the sprites list.

    Args:
        sprites (:obj:`list` of :obj:`list`): the raw sprite data

    Returns:
        a list.
    """
    masked = [sprite_mask(s) for s in sprites if all(s)]
    return masked
    