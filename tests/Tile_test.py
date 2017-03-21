import os
from struct import Struct
import pytest
from cps2 import Tile, ColorTile

TEST_ADDR = ''
TEST_DATA = 'F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4'
TEST_DATA16 = TEST_DATA * 4
TEST_PALETTE_DATA = '100200300510620730840A60C80EA0FB3FD3FE4FF7FFA012FFFFFFFFFFFFFFFF'
ROW_FMT = Struct(8 * 'c')
TILE_PACK_FMT = Struct(32 * 'c')
TILE_UNPACK_FMT = Struct(64 * 'c')

def test_unpack():
    test_data = 'F1' * 32 + 'F2' * 32 + 'F3' * 32 + 'F4' * 32
    tile = Tile.new(TEST_ADDR, bytearray.fromhex(test_data))

    tiles = [tile for tile in TILE_UNPACK_FMT.iter_unpack(tile.data)]
    assert bytearray(b''.join(tiles[0])).hex() == '0f0f0f0f0000000f0f0f0f0f00000f0f' * 4
    assert bytearray(b''.join(tiles[1])).hex() == '0f0f0f0f0000000f0f0f0f0f00000f0f' * 4
    assert bytearray(b''.join(tiles[2])).hex() == '0f0f0f0f00000f000f0f0f0f000f0000' * 4
    assert bytearray(b''.join(tiles[3])).hex() == '0f0f0f0f00000f000f0f0f0f000f0000' * 4

    tile2 = Tile.new(TEST_ADDR, bytearray.fromhex(TEST_DATA), 8)
    assert bytearray(tile2.data).hex() == '0f0f0f0f00080605' * 8

def test_pack():
    tile = Tile.new(TEST_ADDR, bytearray.fromhex(TEST_DATA), '8')

    tile.pack(tile.data)
    for row in ROW_FMT.iter_unpack(tile.data):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

    tile = Tile.new(TEST_ADDR, bytearray.fromhex(TEST_DATA16))

    tile.pack(tile.data)
    for row in ROW_FMT.iter_unpack(tile.data):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

@pytest.fixture(scope='session')
def test_from_image(tmpdir_factory):
    test_data = 'F1' * 32 + 'F2' * 32 + 'F3' * 32 + 'F4' * 32
    tile = Tile.new(TEST_ADDR, bytearray.fromhex(test_data))

    base = tmpdir_factory.mktemp('data')
    fn = base.join('testbmp')
    tile.tobmp(str(fn))

    fn2 = base.join('testbmp.bmp')
    test_tile = Tile.from_image(str(fn2), tile.address)

    assert tile.data == test_tile.data

# Since this was moved inside the Tile class
@pytest.mark.skip
@pytest.mark.parametrize("input, expected", [
    (TEST_DATA, '0f0f0f0f00080605'),
    (TEST_DATA16, '0f0f0f0f00080605'),
])
def test_bitplanes_to_tile(input, expected):
    tile = bytearray.fromhex(input)

    for row in ROW_FMT.iter_unpack(Tile._bitplanes_to_tile(tile)):
        assert bytearray(b''.join(row)).hex() == expected

# Since this was moved inside the Tile class
@pytest.mark.skip
@pytest.mark.parametrize("input, expected", [
    (TEST_DATA, '0f0f0f0f00080605'),
    (TEST_DATA16, '0f0f0f0f00080605'),
])
def test_tile_to_bitplanes(input, expected):
    tile = bytearray.fromhex(TEST_DATA)

    bp = Tile._bitplanes_to_tile(tile)
    for row in ROW_FMT.iter_unpack(Tile._tile_to_bitplanes(bp)):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

# Since this was moved inside the Tile class
@pytest.mark.skip
def test_interleave_subtiles():
    test_data = 'F1' * 32 + 'F2' * 32 + 'F3' * 32 + 'F4' * 32

    interleaved = Tile.Tile._interleave_subtiles(bytearray.fromhex(test_data))

    tiles = [tile for tile in TILE_UNPACK_FMT.iter_unpack(interleaved)]
    assert bytearray(b''.join(tiles[0])).hex() == 'f1f1f1f1f3f3f3f3f1f1f1f1f3f3f3f3' * 4
    assert bytearray(b''.join(tiles[1])).hex() == 'f2f2f2f2f4f4f4f4f2f2f2f2f4f4f4f4' * 4

# Since this was moved inside the Tile class
@pytest.mark.skip
def test_deinterleave_subtiles():
    test_data = 'F1' * 32 + 'F2' * 32 + 'F3' * 32 + 'F4' * 32

    interleaved = _interleave_subtiles(bytearray.fromhex(test_data))
    deinterleaved = _deinterleave_subtiles(interleaved)

    tiles = [tile for tile in TILE_PACK_FMT.iter_unpack(deinterleaved)]
    assert bytearray(b''.join(tiles[0])).hex() == 'f1' * 32
    assert bytearray(b''.join(tiles[1])).hex() == 'f2' * 32
    assert bytearray(b''.join(tiles[2])).hex() == 'f3' * 32
    assert bytearray(b''.join(tiles[3])).hex() == 'f4' * 32

if __name__ == "__main__":
    print("sup")
    