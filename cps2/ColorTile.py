from struct import iter_unpack
import numpy as np
from PIL import Image
from cps2.Tile import Tile

# Tile with 100% more color
# Unpacked and deinterleaved
class ColorTile(Tile):
    def __init__(self, addr, data, palette, dimensions=16):
        super(ColorTile, self).__init__(addr, data, dimensions)
        self._palette = palette
        if palette is not None:
            self._color()

    def __repr__(self):
        return ' '.join(["ColorTile:", str(self._addr), 'size:', str(self._dims)])

    # Does this need to be a protected member?
    def _color(self):
        tile_iter = iter_unpack('c', self._data)
        #refactor this line P L E A S E
        colors = [self._palette[str(int(i[0].hex(), 16))] for i in tile_iter]
        self._data = colors

    # need to turn array of 3 byte RGB values into 3 array of R, G, B
    # then stack them
    def toarray(self):
        """Uses 8x8 or 16x16 Tile data to create an array of the tile's data.

        Returns an array.
        """
        colors = [[], [], []]

        for rgb in self._data:
            colors[0].append(rgb[0])
            colors[1].append(rgb[1])
            colors[2].append(rgb[2])

        arrays = [np.array(c, dtype=np.uint8).reshape((self._dims, self._dims)) for c in colors]
        colorarr = np.dstack(arrays)
        return colorarr

    def tobmp(self, path_to_save):
        """Creates a .bmp image from a single 8x8 or 16x16 tile."""
        try:
            image = Image.fromarray(self.toarray(), 'RGB')
        except ValueError as err:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".bmp")

    def topng(self, path_to_save):
        """Creates a .png image from a single 8x8 or 16x16 tile."""
        try:
            image = Image.fromarray(self.toarray(), 'RGB')
        except ValueError as err:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".png")

    def totile(self):
        """Strips palette.

        Returns interleaved, packed Tile"""
        pass
def new(address, data, palette, dimensions=16):
    return ColorTile(address, data, palette, dimensions)

def fromtile(tile, palette):
    return ColorTile(tile.address, tile.data, palette, tile.dimensions)

# For now just do image -> ColorTile leaving palette info intact.
def from_image(image, address):
    """Given an image returns a ColorTile."""
    im = Image.open(image)
    dims = im.size[0]

    if im.mode == 'P':
        return 'Image is in Palette mode'

    tile_data = list(im.getdata())

    tile = new(address, tile_data, None, dims)

    return tile
