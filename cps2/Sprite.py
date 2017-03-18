import struct
from PIL import Image
import numpy as np
np.set_printoptions(threshold=np.inf)

from cps2 import Tile

#XFLIP/YFLIP not handled yet
#A sprite is a collection of tiles that use the same palette
class Sprite(object):
    def __init__(self, base_tile, tiles, palnum, loc, size, priority=0):
        self._base_tile = base_tile
        self._tiles = tiles
        self._palnum = palnum
        self._loc = loc
        self._size = size
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

        return np.concatenate(array_rows, axis=0)

    # seems to be pulling from wrong palette
    def color_tiles(self, palette):
        """Colors all the tiles"""
        self._tiles = [Tile.fromtile(tile, palette) for tile in self._tiles]

    def tobmp(self, path_to_save):
        """Returns a .bmp file"""
        concat = self.toarray()
        image = Image.fromarray(concat, 'RGB')
        image.save(path_to_save + ".bmp")

    def topng(self, path_to_save):
        """Returns a .png file"""

        concat = self.toarray()
        image = Image.fromarray(concat, 'RGB')
        image.save(path_to_save + ".png")

    def tiles2d(self):
        """Returns a list of lists containing the Sprite's tiles."""
        list_2d = []
        for i in range(self._size[1]):
            offset = self._size[0] * i
            list_2d.append(self._tiles[offset:offset + self._size[0]])

        return list_2d

    def addrs2d(self):
        """Returns a list of lists containing the tiles' addresses."""
        list_2d = []
        for i in range(self._size[1]):
            offset = self._size[0] * i
            list_2d.append([tile.address for tile in self._tiles[offset:offset + self._size[0]]])

        return list_2d

# Factories
def fromdict(dict_):
    """Returns a Sprite object with empty tiles property."""
    palnum = dict_['pal_number']

    tile_number = dict_['tile_number']
    size = (dict_['width'], dict_['height'])
    loc = (dict_['x'], dict_['y'])
    if dict_['offset'] is 0:
        loc = (loc[0] - 64, loc[1] - 16)

    tiles = []
    for i in range(size[1]):
        for j in range(size[0]):
            offset = i * 0x10 + j * 0x1
            addr = hex(int(tile_number, 16) + offset)
            tiles.append(Tile.Tile(addr, None))

    return Sprite(tile_number, tiles, palnum, loc, size, priority=dict_['priority'])

def list2d(list_, size):
    list_2d = []
    for i in range(size[1]):
        offset = size[0] * i
        list_2d.append(list_[offset:offset + size[0]])
    return list_2d
