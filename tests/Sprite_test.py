import mmap
import pytest
import jsonpickle
from cps2 import tile_operations, ColorTile, Sprite

def get_file(fpath):
    return open(fpath, 'r+b')

def get_frame(framefile):
    with open(framefile, 'r') as f:
        data = f.read()
    return jsonpickle.decode(data)

FRAME = get_frame('frame_data\\1141.json')
GFXFILE = get_file('data\\vm3_combined')
GFXMAP = mmap.mmap(GFXFILE.fileno(), 0)

# Make this a real test
# should supply a test input + palette and check output
# @pytest.mark.skip
def test_colortile():
    sprite = FRAME.sprites[0]
    palette = FRAME.palettes[sprite.palnum]
    sprite.tiles = tile_operations.read_tiles_from_file(GFXFILE, sprite.tiles)
    sprite.color_tiles(palette)

# WORKS
# Not a real test though
# @pytest.mark.skip
def test_topng():
    for i, sprite in enumerate(FRAME.sprites):
        palette = FRAME.palettes[sprite.palnum]
        FRAME.sprites[i].tiles = tile_operations.read_tiles_from_file(GFXMAP, sprite.tiles)
        sprite.color_tiles(palette)
        sprite.topng('\\'.join(['frame_img', str(sprite.base_tile)]))
    # FRAME.topng('\\'.join(['frame_img', str(FRAME.fnumber)]))
    # assert 0

# Currently only tests ColorTile
# @pytest.fixture(scope='session')
# @pytest.mark.skip
def test_from_image_colortile(tmpdir_factory):
    sprite = FRAME.sprites[0]
    palette = FRAME.palettes[sprite.palnum]
    sprite.tiles = tile_operations.read_tiles_from_file(GFXFILE, sprite.tiles)
    sprite.color_tiles(palette)

    tile = sprite.tiles[0]

    base = tmpdir_factory.mktemp('data')
    fn = base.join('colortestpng')
    tile.topng(str(fn))

    fn2 = base.join('colortestpng.png')
    test_tile = ColorTile.from_image(str(fn2), tile.address)

    assert tile.data == test_tile.data

def test_totile():
    for sprite in FRAME.sprites:
        palette = FRAME.palettes[sprite.palnum]
        sprite.tiles = tile_operations.read_tiles_from_file(GFXFILE, sprite.tiles)
        basetiles = sprite.tiles

        sprite.color_tiles(palette)
        for i, tile in enumerate(sprite.tiles):
            stripped = tile.totile()
            assert basetiles[i] == stripped

# @pytest.fixture(scope='session')
# @pytest.mark.skip
def test_from_image(tmpdir_factory):
    for sprite in FRAME.sprites:
        palette = FRAME.palettes[sprite.palnum]
        sprite.tiles = tile_operations.read_tiles_from_file(GFXFILE, sprite.tiles)
        sprite.color_tiles(palette)
        base = tmpdir_factory.mktemp('data')
        fn = base.join('spritetestpng')
        sprite.topng(str(fn))

        fn2 = base.join('spritetestpng.png')
        test_sprite = Sprite.from_image(str(fn2), sprite)

        for tile1, tile2 in zip(sprite.tiles, test_sprite.tiles):
            assert tile1 == tile2

