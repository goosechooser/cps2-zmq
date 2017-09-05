from struct import Struct
import pytest
from cps2_zmq.process import Tile

TEST_ADDR = ''
TEST_DATA = 'F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4'
TEST_DATA16 = TEST_DATA * 4
TEST_PALETTE_DATA = '100200300510620730840A60C80EA0FB3FD3FE4FF7FFA012FFFFFFFFFFFFFFFF'
ROW_FMT = Struct(8 * 'c')
TILE_PACK_FMT = Struct(32 * 'c')
TILE_UNPACK_FMT = Struct(64 * 'c')

def test_from_packed_bytes():
    test_data = 'F1' * 32 + 'F2' * 32 + 'F3' * 32 + 'F4' * 32

    tile = Tile.from_packed_bytes(TEST_ADDR, bytearray.fromhex(test_data))

    tiles = [t for t in TILE_UNPACK_FMT.iter_unpack(tile.data)]
    assert bytearray(b''.join(tiles[0])).hex() == '0f0f0f0f0000000f0f0f0f0f00000f0f' * 4
    assert bytearray(b''.join(tiles[1])).hex() == '0f0f0f0f0000000f0f0f0f0f00000f0f' * 4
    assert bytearray(b''.join(tiles[2])).hex() == '0f0f0f0f00000f000f0f0f0f000f0000' * 4
    assert bytearray(b''.join(tiles[3])).hex() == '0f0f0f0f00000f000f0f0f0f000f0000' * 4

    tile2 = Tile.from_packed_bytes(TEST_ADDR, bytearray.fromhex(TEST_DATA), dimensions=8)
    assert bytearray(tile2.data).hex() == '0f0f0f0f00080605' * 8

def test_pack():
    tile = Tile.from_packed_bytes(TEST_ADDR, bytearray.fromhex(TEST_DATA), dimensions=8)

    tile.pack(tile.data)
    for row in ROW_FMT.iter_unpack(tile.data):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

    tile = Tile.from_packed_bytes(TEST_ADDR, bytearray.fromhex(TEST_DATA16))

    tile.pack(tile.data)
    for row in ROW_FMT.iter_unpack(tile.data):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

@pytest.fixture(scope='session')
def test_from_image(tmpdir_factory):
    test_data = 'F1' * 32 + 'F2' * 32 + 'F3' * 32 + 'F4' * 32
    tile = Tile(TEST_ADDR, bytearray.fromhex(test_data))

    base = tmpdir_factory.mktemp('data')
    fn = base.join('testbmp')
    tile.to_bmp(str(fn))

    fn2 = base.join('testbmp.bmp')
    test_tile = Tile.from_image(str(fn2), tile.address)

    assert tile.data == test_tile.data
