from src.processing import Tile

# tile_operations.py handles I/O tasks
# ie: reading tile data or writing tile data out

# MMAP is not thread safe
# Will need to consider memoization or some sort of cache?
# How to best prep data before reading from this
def read_tiles_from_file(gfxfile, unfilled, fsplit=False):
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

# Currently assumes end file is combination of 2 halves
def write_tiles_to_file(tiles, gfx_file, output_file=None):
    """Writes tile data to a given file."""
    if output_file is None:
        output_file = gfx_file + '_edit'

    sorted_tiles = sorted(tiles, key=lambda tile: int(tile.address, 16))

    with open(gfx_file, 'rb') as gfx_reader:
        with open(output_file, 'wb') as f:
            for tile in sorted_tiles:
                converted_addr = convert_mame_addr(tile.address, tile.dimensions)
                read_length = converted_addr - gfx_reader.tell()
                if read_length == 128:
                    gfx_reader.seek(read_length, 1)
                    f.write(tile.data)
                else:
                    unchanged_gfx = gfx_reader.read(read_length)
                    f.write(unchanged_gfx)
                    gfx_reader.seek(128, 1)
                    f.write(tile.data)

            final_read = gfx_reader.read()
            f.write(final_read)

def convert_mame_addr(mame_addr, tile_size, split=True):
    """Converts the address value MAME displays when you press 'F4'.

    Returns an int.
    """
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
