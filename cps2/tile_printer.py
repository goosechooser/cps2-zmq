# from PIL import Image
import numpy as np
from cps2 import Tile

#TilePrinter is currently responsible for:
#read combined eprom file(s) -> create tile(s) -> convert to array(s) -> create bmp(s)

#Eventually should be responsible for:
#pass in tiles [created elsewhere] -> convert to array(s) -> create bmp(s)

#Changing to arrays allows for more flexible processing of 16x16 tiles
#without mucking around at a lower level
#Ideas for glitchy tileset -> just rearrage all the tiles and write back like regular

#the way a group of 16x16 tiles is given, is how the final picture is assembled
#example of how addresses are formatted
#addrs = [['blank', '2F810',],
#         ['blank', '2F820',]]

# MMAP is not thread safe
# Will need to consider memoization or some sort of cache?
# How to best prep data before reading from this
def fill_tiles(gfxfile, unfilled, fsplit=False):
    """Pass a file handler. Given a list of Tiles, fills in data

    Returns a list of Tiles
    """

    filled = []
    for tile in unfilled:
        if tile.address.upper() != 'BLANK':
            gfxfile.seek(convert_mame_addr(tile.address, tile.dimensions, fsplit))
            if tile.dimensions == 8:
                read_data = gfxfile.read(32)
            if tile.dimensions == 16:
                read_data = gfxfile.read(128)
            filled.append(Tile.new(tile.address, read_data, tile.dimensions))

    return filled

def convert_mame_addr(mame_addr, tile_size, split=True):
    """Converts the address value MAME displays when you press 'F4'.

    Returns an int.
    """
    tile_bytes = 0
    addr = int(mame_addr, 16)
    if tile_size == 8:
        tile_bytes = 32
    if tile_size == 16:
        tile_bytes = 128

    converted_addr = addr * tile_bytes

    if not split:
        return converted_addr
    memory_bank_size = int('0x1000000', 16)

    #currently the 8 eproms are split into 2 banks
    if converted_addr > memory_bank_size:
        converted_addr -= memory_bank_size

    return converted_addr

#Should make this so it only needs a list of tiles and a path to save the image
def process_tile_order(tiles):
    """Stitches multiple Tiles together into one array suitable for producing an image file.

    Returns an np.array.
    """
    pic_array = []
    for row_of_tiles in tiles:
        row = []
        for tile in row_of_tiles:
            row.append(tile.toarray())

        pic_array.append(row)

    return pic_array

def concat_arrays(arrays):
    """Concatenates a 2D list of arrays into one array.

    Returns an array.
    """
    array_rows = []
    for row in arrays:
        array_rows.append(np.concatenate(row, axis=1))
    assembled = np.concatenate(array_rows, axis=0)

    return assembled

# def gfx_to_bmp(gfx_file, addresses, output_image, tile_dim=16):
#     """Encapsulates all the seperate steps.
#     Produces a BMP file.
#     """
#     tiles = make_tiles(gfx_file, addresses, tile_dim)
#     pic_array = process_tile_order(tiles)
#     assembled = concat_arrays(pic_array)

#     image = Image.fromarray(assembled, 'P')

#     image.save(output_image)
