from PIL import Image
import numpy as np
np.set_printoptions(threshold=np.inf)

from cps2_zmq.process import Tile, ColorTile

class Sprite(object):
    """
    A Sprite encapsulates a collection of :py:mod:`~cps2_zmq.gather.Tile.Tile` that use the same palette.

    Attributes:
        base_tile (str): the address in memory of the first :py:mod:`~cps2_zmq.gather.Tile.Tile` in the grouping
        tiles (:obj:`list` of :py:mod:`~cps2_zmq.gather.Tile.Tile`): a list of Tiles that make up the Sprite
        palnum (int): which of the 32 palettes in a Frame the Sprite uses
        loc (int, int): the (x,y) coordinate where the Sprite will be drawn on the screen
        size (int, int): (width, height) the size of the Sprite in Tiles.
            (1, 1) means a single Tile.
        flips (int, int): (xflip, yflip) determines whether the Sprite needs to be flipped over its X or Y axis.
        priority (int): determines what other Sprites will be covered or which Sprites will cover this Sprite.
            0 is lowest, 3 is highest.
    """
    def __init__(self, base_tile, tiles, palnum, loc, size, flips, priority=0):
        self._base_tile = base_tile
        self._tiles = tiles
        self._palnum = palnum
        self._loc = loc
        self._size = size
        self._flips = flips
        self._priority = priority

    def __repr__(self):
        addrs = [tile.address for tile in self._tiles if tile]
        loc = " Location: (" + str(self._loc[0]) + ", " + str(self._loc[1])
        size = " Size: (" + str(self._size[0]) + ", " + str(self._size[1])
        return "Sprite contains tiles: " + str(addrs) + loc + ")" + size + ")"

    @property
    def base_tile(self):
        return self._base_tile

    @base_tile.setter
    def base_tile(self, value):
        self._base_tile = value

    @property
    def tiles(self):
        return self._tiles

    @tiles.setter
    def tiles(self, value):
        self._tiles = value

    @property
    def palnum(self):
        return self._palnum

    @palnum.setter
    def palnum(self, value):
        self._palnum = value

    @property
    def location(self):
        return self._loc

    @location.setter
    def location(self, value):
        self._loc = value

    @property
    def size(self):
        return self._size

    @property
    def flips(self):
        return self._flips

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = value

    def height(self):
        return self._size[1]

    def width(self):
        return self._size[0]

    def toarray(self, flip=True):
        """
        Provides contents of Sprite as a numpy array.
        Does any necessary flips in the process.

        Args:
            flip (bool, optional): Whether or not the Sprite contents are flipped. Defaults to True.

        Returns:
            a 2D numpy array.
        """

        arrays = [tile.toarray() for tile in self._tiles]
        array2d = list2d(arrays, self._size)
        array_rows = [np.concatenate(row, axis=1) for row in array2d]
        preflip = np.concatenate(array_rows, axis=0)

        if flip and self._flips[0]:
            preflip = np.fliplr(preflip)
        if flip and self._flips[1]:
            preflip = np.flipud(preflip)

        return preflip

    def color_tiles(self, palette):
        """
        Converts any :obj:`Tile` the :obj:`Sprite` has into :obj:`ColorTile`.

        Args:
            palette (dict): the palette to use.
        """

        self._tiles = [ColorTile.from_tile(tile, palette)
                       for tile in self._tiles
                       if isinstance(tile, Tile.Tile)]

    def tobmp(self, path_to_save):
        """
        Creates a .bmp file
        """
        try:
            image = Image.fromarray(self.toarray(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".bmp")

    def topng(self, path_to_save):
        """
        Creates a .png file
        """
        try:
            image = Image.fromarray(self.toarray(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".png")

    def totile(self):
        """
        This method is *probably* used when writing the contents of the :obj:`Sprite` to file.
        Converts any :obj:`ColorTile` objects the :obj:`Sprite` has to :obj:`Tile` objects.

        Returns:
            a list of Tiles.
        """
        return [t.totile() if isinstance(t, ColorTile.ColorTile) else t for t in self.tiles]

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
def fromdict(dict_):
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

def to_file():
    pass
