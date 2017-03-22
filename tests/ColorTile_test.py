import pytest
from src.processing import tile_operations, ColorTile

# from src import processing
# @pytest.fixture(scope='session')
# @pytest.mark.skip
def test_from_image_colortile(tmpdir_factory, testframe, gfxfile):
    sprite = testframe.sprites[0]
    palette = testframe.palettes[sprite.palnum]
    sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)
    sprite.color_tiles(palette)

    tile = sprite.tiles[0]

    base = tmpdir_factory.mktemp('data')
    fn = base.join('colortestpng')
    tile.topng(str(fn))

    fn2 = base.join('colortestpng.png')
    test_tile = ColorTile.from_image(str(fn2), tile.address)

    assert tile.data == test_tile.data

def test_totile(testframe, gfxfile):
    for sprite in testframe.sprites:
        palette = testframe.palettes[sprite.palnum]
        sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)
        basetiles = sprite.tiles

        sprite.color_tiles(palette)
        for i, tile in enumerate(sprite.tiles):
            stripped = tile.totile()
            assert basetiles[i] == stripped
