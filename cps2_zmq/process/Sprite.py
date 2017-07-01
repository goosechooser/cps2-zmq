import jsonpickle
from PIL import Image
import numpy as np

from cps2_zmq.process import Tile, ColorTile, GraphicAsset

class Sprite(GraphicAsset.GraphicAsset):
    """
    A Sprite is a grouping of :py:mod:`~cps2_zmq.gather.Tile.Tile` that use the same palette.

    Attributes:
        base_tile (str): the memory address of the first :py:mod:`~cps2_zmq.gather.Tile.Tile`
        tiles (:obj:`list` of :py:mod:`~cps2_zmq.gather.Tile.Tile`): Tiles that make up the Sprite
        palnum (int): which of the 32 palettes in a Frame the Sprite uses
        location (int, int): the (x,y) coordinate where the Sprite will be drawn on the screen
        size (int, int): (width, height) the size of the Sprite in Tiles. (1, 1) means a single Tile
        flips (int, int): (flipx, flipy) determines if the Sprite is flipped over its X or Y axis
        priority (int): determines which layer the Sprite is displayed on. 0 is lowest, 3 is highest
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

    def color_tiles(self, palette):
        """
        Converts any :obj:`Tile` the :obj:`Sprite` has into :obj:`ColorTile`.

        Args:
            palette (dict): the palette to use.
        """

        self.tiles = [ColorTile.from_tile(tile, palette)
                      for tile in self.tiles
                      if isinstance(tile, Tile.Tile)]

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

    def to_tile(self):
        """
        This method is *probably* used when writing the contents of the :obj:`Sprite` to file.
        Converts any :obj:`ColorTile` objects the :obj:`Sprite` has to :obj:`Tile` objects.

        Returns:
            a list of Tiles.
        """
        return [t.to_tile() if isinstance(t, ColorTile.ColorTile) else t for t in self.tiles]
        
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

    dict_['tiles'] = generate_tiles(dict_['base_tile'], dict_['size'])

    return Sprite(**dict_)


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

    top_half = "{0:#x}".format((byte_data[1] & 0x6000) >> 13)
    bottom_half = "{0:x}".format(byte_data[2])
    dict_['base_tile'] = ''.join([top_half, bottom_half])
    tile_height = ((byte_data[3] & 0xF000) >> 12) + 1
    tile_width = ((byte_data[3] & 0x0F00) >> 8) + 1
    dict_['size'] = (tile_width, tile_height)

    #(0 = Offset by X:-64,Y:-16, 1 = No offset)
    offset = (byte_data[3] & 0x0080) >> 7
    location_x = byte_data[0] & 0x03FF
    location_y = byte_data[1] & 0x03FF

    if not offset:
        location_x -= 64
        location_y -= 16

    dict_['location'] = (location_x, location_y)
    #Y flip, X flip (1= enable, 0= disable)
    flip_x = (byte_data[3] & 0x0040) >> 69
    flip_y = (byte_data[3] & 0x0020) >> 5
    dict_['flips'] = (flip_x, flip_y)
    dict_['palnum'] = "{0:d}".format(byte_data[3] & 0x001F)

    # Keeping these because maybe I'll need them one day
    # dict_['eol'] = (byte_data[1] & 0x8000) >> 15
    # dict_['mem_addr'] = "{0:x}".format(byte_data[4])

    return dict_

def generate_tiles(tile_number, size):
    """
    Fills in the rest of the Tile info for a Sprite.

    Args:
        tile_number (str): the memory address of the base tile
        size ((int, int)): the size of the Sprite

    Return:
        a list of Tile.
    """
    tiles = []
    for i in range(size[1]):
        for j in range(size[0]):
            offset = i * 0x10 + j * 0x1
            addr = hex(int(tile_number, 16) + offset)
            tiles.append(Tile.Tile(addr, None))

    return tiles

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

    try:
        tiles = [ColorTile.new(addr, list(img.getdata()), None) for img, addr in zipped]
    except ValueError:
        tiles = [Tile.new(addr, bytes(img.getdata())) for img, addr in zipped]

    new_sprite = sprite
    new_sprite.tiles = tiles
    return new_sprite
    