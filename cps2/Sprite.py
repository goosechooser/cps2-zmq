from PIL import Image
import numpy as np
np.set_printoptions(threshold=np.inf)

from cps2 import Tile, ColorTile

#A sprite is a collection of tiles that use the same palette
class Sprite(object):
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

    def toarray(self):
        """Returns contents of Sprite as a numpy array."""

        arrays = [tile.toarray() for tile in self._tiles]
        array2d = list2d(arrays, self._size)
        array_rows = [np.concatenate(row, axis=1) for row in array2d]
        preflip = np.concatenate(array_rows, axis=0)

        if self._flips[0]:
            preflip = np.fliplr(preflip)
        if self._flips[1]:
            preflip = np.flipud(preflip)

        return preflip

    def color_tiles(self, palette):
        """Colors all the tiles"""

        self._tiles = [ColorTile.from_tile(tile, palette) for tile in self._tiles]

    def tobmp(self, path_to_save):
        """Creates a .bmp file"""
        try:
            image = Image.fromarray(self.toarray(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".bmp")

    def topng(self, path_to_save):
        """Creates a .png file"""
        try:
            image = Image.fromarray(self.toarray(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".png")

    def totile(self):
        """Returns list of Tiles."""
        return [t.totile() if isinstance(t, ColorTile.ColorTile) else t for t in self.tiles]

def list2d(list_, size):
    list_2d = []
    for i in range(size[1]):
        offset = size[0] * i
        list_2d.append(list_[offset:offset + size[0]])
    return list_2d

# Factories
def fromdict(dict_):
    """Returns a Sprite object with empty tiles property."""
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
    """Given an image and a Sprite, returns a Sprite."""
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
