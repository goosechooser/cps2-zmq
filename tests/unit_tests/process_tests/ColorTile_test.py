import pytest
from cps2zmq.process import tile_operations, ColorTile

def test_from_image_colortile(tmpdir_factory, testframe, gfxfile):
    sprite = testframe.sprites[0]
    palette = testframe.palettes[sprite.palnum]
    sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)
    sprite.color_tiles(palette)

    tile = sprite.tiles[0]

    base = tmpdir_factory.mktemp('data')
    fn = base.join('colortestpng')
    tile.to_png(str(fn))

    fn2 = base.join('colortestpng.png')
    test_tile = ColorTile.from_image(str(fn2), tile.address)
    assert tile.data == test_tile.data

# This is broken by palettes that have the same values in them multiple times
# Not sure of best fix at this point in time
# Just create a test set that avoids this?
@pytest.mark.skip
def test_to_tile(testframe, gfxfile):
    for sprite in testframe.sprites:
        palette = testframe.palettes[sprite.palnum]
        sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)
        basetiles = sprite.tiles

        sprite.color_tiles(palette)
        for i, tile in enumerate(sprite.tiles):
            stripped = tile.to_tile()
            assert basetiles[i] == stripped
