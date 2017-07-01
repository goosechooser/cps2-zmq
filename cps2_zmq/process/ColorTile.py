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
            address (int): the address in memory the tile resides at.
            data (:obj:`bytes`): 32 bytes for a 8x8 tile or 128 bytes for a 16x16 tile.
            palette (dict): 16 key-value pairs related to what the RGB value of a pixel is.
            dimensions (int): 8 for an 8x8 tile, 16 for a 16x16 tile.
    """
    def __init__(self, address, data, palette, dimensions=16):
        """
        Constructs a new :obj:`ColorTile` object.
        """
        super(ColorTile, self).__init__(address, data, dimensions)
        self.palette = palette
        if self.palette is not None:
            self.color()

    def __repr__(self):
        return ' '.join(["ColorTile:", str(self.address), 'size:', str(self.dimensions)])

    # todo: exception handling for palettes that don't have the correct key(s)
    def color(self):
        tile_iter = iter_unpack('c', self.data)
        colors = [self.palette[int.from_bytes(i[0], byteorder='big')] for i in tile_iter]
        self.data = colors

    def to_array(self):
        """
        Converts the :obj:`ColorTile` data into a correctly shaped numpy array.

        Returns:
            a numpy.array.
        """
        colors = [[], [], []]

        for rgb in self.data:
            colors[0].append(rgb[0])
            colors[1].append(rgb[1])
            colors[2].append(rgb[2])

        arrays = [np.array(c, dtype=np.uint8).reshape((self.dimensions, self.dimensions)) for c in colors]
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
    
    # Broken atm
    def to_tile(self):
        """
        Removes the RGB pixel values from the :obj:`ColorTile`.

        Returns:
            a new unpacked :obj:`Tile`.
        """
        reversed_ = dict((i, v) for i, v in enumerate(self.palette))
        stripped = [int(reversed_[d]) for d in self.data]

        return Tile(self.address, bytes(stripped))

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

    tile_data = list(map(list, im.getdata()))

    tile = new(address, tile_data, None, dims)

    return tile
