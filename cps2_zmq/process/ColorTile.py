from struct import iter_unpack
import numpy as np
from PIL import Image
from cps2_zmq.process.Tile import Tile

# Tile with 100% more color
# Unpacked and deinterleaved
class ColorTile(Tile):
    """
    ColorTile is Tile with a color palette.

    Attributes:
            addr (int): the address in memory the tile resides at.
            data (:obj:`bytes`): 32 bytes for a 8x8 tile or 128 bytes for a 16x16 tile.
            dimensions (int): 8 for an 8x8 tile, 16 for a 16x16 tile.
            palette (dict): 16 key-value pairs related to what the RGB value of a pixel is.
    """
    def __init__(self, addr, data, palette, dimensions=16):
        """
        Constructs a new :obj:`ColorTile` object.
        """
        super(ColorTile, self).__init__(addr, data, dimensions)
        self._palette = palette
        if palette is not None:
            self._color()

    def __repr__(self):
        return ' '.join(["ColorTile:", str(self._addr), 'size:', str(self._dims)])

    # todo: exception handling for palettes that don't have the correct key(s)
    def _color(self):
        tile_iter = iter_unpack('c', self._data)
        colors = [self._palette[str(int.from_bytes(i[0], byteorder='big'))] for i in tile_iter]
        self._data = colors

    def to_array(self):
        """
        Converts the :obj:`ColorTile` data into a correctly shaped numpy array.

        Returns:
            a numpy.array.
        """
        colors = [[], [], []]

        for rgb in self._data:
            colors[0].append(rgb[0])
            colors[1].append(rgb[1])
            colors[2].append(rgb[2])

        arrays = [np.array(c, dtype=np.uint8).reshape((self._dims, self._dims)) for c in colors]
        colorarr = np.dstack(arrays)
        return colorarr

    def to_bmp(self, path):
        """
        Creates a .bmp image.

        Args:
            path (str): the location to save to
        """
        try:
            image = Image.fromarray(self.to_array(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.to_array(), 'P')
        image.save(path + ".bmp")

    def to_png(self, path):
        """
        Creates a .png image from a single 8x8 or 16x16 tile.

        Args:
            path (str): the location to save to
        """
        try:
            image = Image.fromarray(self.to_array(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.to_array(), 'P')
        image.save(path + ".png")

    def to_tile(self):
        """
        Removes the RGB pixel values from the :obj:`ColorTile`.

        Returns:
            a new unpacked :obj:`Tile`.
        """
        reversed_ = {v : k for k, v in self._palette.items()}
        stripped = [int(reversed_[d]) for d in self._data]

        return Tile(self._addr, bytes(stripped))

def new(address, data, palette, dimensions=16):
    """
    A factory function.

    Returns:
        a :obj:`ColorTile`.
    """
    return ColorTile(address, data, palette, dimensions)

def from_tile(tile, palette):
    """
    A factory function.

    Args:
        tile (:obj:`Tile`): the :obj:`Tile` to be colored.
        palette (dict): the color palette.

    Returns:
        a :obj:`ColorTile`.
    """
    return ColorTile(tile.address, tile.data, palette, tile.dimensions)

# For now just do image -> ColorTile leaving palette info intact.
def from_image(image, address):
    """
    A factory function.

    Args:
        image (str): path to image
        address (str): address in memory of :obj:`ColorTile`.

    Returns:
        a :obj:`ColorTile`.
    """
    im = Image.open(image)
    dims = im.size[0]

    if im.mode == 'P':
        return 'Image is in Palette mode'

    tile_data = list(im.getdata())

    tile = new(address, tile_data, None, dims)

    return tile
