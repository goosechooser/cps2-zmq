from struct import iter_unpack
import numpy as np
from PIL import Image
from src.processing.Tile import Tile

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
        colors = [self._palette[str(int.from_bytes(i[0], byteorder='big'))] for i in tile_iter]
        self._data = colors

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
        except ValueError:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".bmp")

    def topng(self, path_to_save):
        """Creates a .png image from a single 8x8 or 16x16 tile."""
        try:
            image = Image.fromarray(self.toarray(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".png")

    def totile(self):
        """Strips palette. Returns new unpacked Tile"""
        reversed_ = {v : k for k, v in self._palette.items()}
        stripped = [int(reversed_[d]) for d in self._data]

        return Tile(self._addr, bytes(stripped))

def new(address, data, palette, dimensions=16):
    return ColorTile(address, data, palette, dimensions)

def from_tile(tile, palette):
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
