from struct import Struct
from PIL import Image
import numpy as np
from cps2_zmq.process.GraphicAsset import GraphicAsset

# Need to clean this file up
class Tile(GraphicAsset):
    """
    * Tile is a container for all the good stuff associated with the graphical tiles used by the CPS2
    * Graphical tiles used by the CPS2 are sized 8x8, 16x16, or 32x32 (currently not supported by this project)
    * Tiles are packed using the 4BPP format. When unpacked a pixel's 'value' will range 0-15
    * 8x8 tiles are 32 bytes long when packed, 64 bytes long when unpacked
    * 16x16 tiles are made up of 4 8x8 tiles and these subtiles are row interleaved. ex: [[tile1, tile3], [tile2, tile4]]

    Attributes:
            address (int): the address in memory the tile resides at.
            data (:obj:`bytes`): 32 bytes for a 8x8 tile or 128 bytes for a 16x16 tile.
            dimensions (int): 8 for an 8x8 tile, 16 for a 16x16 tile.
    """
    def __init__(self, address, data, dimensions=16):
        self.address = address
        self.data = data
        self.dimensions = dimensions

    def __eq__(self, other):
        return self.address == other.address and self.data == other.data

    def __repr__(self):
        return ' '.join(["Tile:", str(self.address), 'size:', str(self.dimensions)])



    def unpack(self):
        """
        Unpacks the Tile's data. If its a 16x16 tile, deinterleaves the 8x8 subtiles.
        This converts the 4BPP values used by the CPS2 into 'pixel' values (0-15).

        Returns:
            a :obj:`bytes` of the unpacked data.
        """
        tile_fmt = Struct(32 * 'c')
        tile_iter = tile_fmt.iter_unpack(self.data)

        # need to interleave the 4 8x8 tiles in a 16x16 tile
        if self.dimensions == 16:
            interleaved = Tile._interleave_subtiles(self.data)
            iter_ = tile_fmt.iter_unpack(interleaved)
        else:
            tile_fmt = Struct(32 * 'c')
            tile_iter = tile_fmt.iter_unpack(self.data)
            iter_ = tile_iter

        tiles = [Tile._bitplanes_to_tile(b''.join(tile)) for tile in iter_]
        return b''.join(tiles)

    # Converts contents, then rearranges innter 8x8 tiles
    def pack(self, data):
        """
        Converts 'pixel' values (0-15) into the 4BPP format.
        If its a 16x16 Tile, interleaves the 8x8 subtiles.

        Args:
            data (:obj:`bytes`): the data to be packed into the Tile
        """

        #Need exception handling for packing incorrectly sized data
        tile_fmt = Struct(32 * 'c')
        tile_iter = tile_fmt.iter_unpack(data)

        vals = [Tile._tile_to_bitplanes(b''.join(tile)) for tile in tile_iter]
        self.data = b''.join(vals)

        if self.dimensions == 16:
            self.data = Tile._deinterleave_subtiles(self.data)

    def to_array(self):
        """
        Converts the :obj:`Tile` data into a correctly shaped numpy array.

        Returns:
            a numpy.array
        """
        arr = np.frombuffer(self.data, dtype=np.uint8).reshape((self.dimensions, self.dimensions))
        return arr

    # unpacking tiles
    @staticmethod
    def _bitplanes_to_tile(data):
        """
        A private method.

        Unpacks the 4BPP values and converts them to pixel values.
        Args:
            data (:obj:`bytes`): 32 bytes of 4BPP data
        Returns:
            a :obj:`bytes` of length 64 for an 8x8 tile
        """
        bitplanes = Tile._unpack_bitplanes(data)

        pixels = []
        for i in range(0, 8):
            temp_val = [bitplanes[0][i], bitplanes[1][i],
                        bitplanes[2][i], bitplanes[3][i]]
            row = Tile._make_row_of_pixels(temp_val)

            pixels.append(row)

        return b''.join(pixels)

    @staticmethod
    def _unpack_bitplanes(data):
        """
        A private method.

        The 4BPP values that make up a row of pixels are organized like:
        [bp1-row1] [bp2-row1] [bp3-row1] [bp4-row1]...
        [bp1-row8] [bp2-row8] [bp3-row8] [bp4-row8]

        Args:
            data (:obj:`bytes`):

        Returns:
            a :obj:`list` of 4 :obj:`list` containing bitplane values (:obj:`bytes`) organized like:
            [bp1-row1] .. [bp1-row8]
            [bp2-row1] .. [bp2-row8]
            [bp3-row1] .. [bp3-row8]
            [bp4-row1] .. [bp4-row8]
        """
        planes = [[], [], [], []]
        data_iter = Struct('cccc').iter_unpack(data)

        for bp in data_iter:
            planes[0].extend(bp[0])
            planes[1].extend(bp[1])
            planes[2].extend(bp[2])
            planes[3].extend(bp[3])

        return planes

    @staticmethod
    def _make_row_of_pixels(bitplane_rows):
        """
        A private method.

        Converts the 4 bytes of bitplanes 1-4 for a given row into a row of pixel values

        Args:
            bitplane_rows (:obj:`list` of :obj:`list`): 4 lists containing 8 lists of 4BPP values

        Returns:
            :obj:`bytes`
        """
        mask = int(b'00000001')
        row_of_pixels = []
        for _ in range(0, 8):
            masked = [value & mask for value in bitplane_rows]
            bitplane_rows = [value >> 1 for value in bitplane_rows]
            bitplane_values = masked[3] << 3 | masked[2] << 2 | masked[1] << 1 | masked[0]
            row_of_pixels.append(bitplane_values.to_bytes(1, byteorder='big'))

        row_of_pixels.reverse()

        return b''.join(row_of_pixels)

    # packing tiles
    @staticmethod
    def _tile_to_bitplanes(data):
        bitplanes = []
        row_fmt = Struct(8 * 'c')
        row_iter = row_fmt.iter_unpack(data)

        bitplanes = [Tile._pixel_row_to_4bpp(row) for row in row_iter]

        return b''.join(bitplanes)

    @staticmethod
    def _pixel_row_to_4bpp(row):
        bitplanes = [0, 0, 0, 0]
        mask = int(b'00000001')
        row = [int.from_bytes(val, byteorder='big') for val in row]

        for pixel in row:
            for i, plane in enumerate(bitplanes):
                bitplanes[i] = (plane << 1) | (pixel & mask)
                pixel = pixel >> 1

        return bytearray(bitplanes)

    # Would need to interleave like:
    # [subtile1-row1] [subtile3-row1]
    # [subtile1-row16] [subtile3-row16]
    # [subtile2-row1] [subtile4-row1]
    # [subtile4-row16] [subtile4-row16]
    @staticmethod
    def _interleave_subtiles(tiledata):
        """Row interleaves the 4 8x8 subtiles in a 16x16 tile.

        Returns bytes().
        """
        tile_fmt = Struct(32 * 'c')
        tile_iter = tile_fmt.iter_unpack(tiledata)

        subtiles = [b''.join(subtile) for subtile in tile_iter]

        top = Tile._interleave(subtiles[0], subtiles[2])
        bottom = Tile._interleave(subtiles[1], subtiles[3])

        interleaved = [*top, *bottom]
        return b''.join(interleaved)

    @staticmethod
    def _interleave(subtile1, subtile2):
        """Interleaves two 8x8 tiles like
        [subtile1-row1] [subtile2-row1] ...
        [subtile1-row16] [subtile2-row16]

        Returns bytes()
        """
        interleaved = []
        interleave_fmt = Struct(4 * 'c')

        left_iter = interleave_fmt.iter_unpack(subtile1)
        right_iter = interleave_fmt.iter_unpack(subtile2)

        for i in left_iter:
            right_next = next(right_iter)
            interleaved.extend([*i, *right_next])

        return interleaved

    @staticmethod
    def _deinterleave_subtiles(data):
        tile_fmt = Struct(64 * 'c')
        tile_iter = tile_fmt.iter_unpack(data)

        subtiles = []
        for subtile in tile_iter:
            subtiles.extend(Tile._deinterleave(b''.join(subtile)))

        deinterleaved = [subtiles[0], subtiles[2], subtiles[1], subtiles[3]]
        return b''.join(deinterleaved)

    @staticmethod
    def _deinterleave(data):
        deinterleaved = [[], []]

        deinterleave_fmt = Struct(4 * 'c')
        deinterleave_iter = deinterleave_fmt.iter_unpack(data)

        for i in deinterleave_iter:
            deinterleaved[0].extend([*i])
            deinterleaved[1].extend([*next(deinterleave_iter)])

        return [b''.join(data) for data in deinterleaved]

# Factories
def new(addr, data, dimensions=16):
    tile = Tile(addr, data, dimensions)
    if tile.data is not None:
        tile.data = tile.unpack()
    return tile

def from_dict(dict_):
    """
    A factory function.

    Args:
        dict_ (dict): dict containing the following keys: 'address', 'data', and 'dimensions'

    Returns:
        a Tile
    """

    return Tile(dict_['address'], dict_['data'], dict_['dimensions'])

def from_image(image, address):
    """
    A factory function.

    Args:
        image (str): path to image
        address (str): address in memory of Tile

    Returns:
        a Tile
    """
    im = Image.open(image)
    dims = im.size[0]

    tile = new(address, None, dims)
    tile.data = bytes(im.getdata())
    return tile

class EmptyTile(Tile):
    """
    EmptyTile is a placeholder.
    """
    def __init__(self, dimensions):
        super().__init__('BLANK', None, dimensions)

    def to_array(self):
        zero = int('0x20', 16).to_bytes(1, byteorder='big')
        row = [zero] * self.dimensions
        tile = [row] * self.dimensions

        return np.array(tile)



