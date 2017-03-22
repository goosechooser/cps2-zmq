import pytest
from src.processing import tile_operations, Sprite

# Make this a real test
# should supply a test input + palette and check output
# @pytest.mark.skip
def test_colortile(testframe, gfxfile):
    sprite = testframe.sprites[0]
    palette = testframe.palettes[sprite.palnum]
    sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)
    sprite.color_tiles(palette)

# WORKS
# Not a real test though
# @pytest.mark.skip
def test_topng(testframe, gfxmap):
    for i, sprite in enumerate(testframe.sprites):
        palette = testframe.palettes[sprite.palnum]
        testframe.sprites[i].tiles = tile_operations.read_tiles_from_file(gfxmap, sprite.tiles)
        sprite.color_tiles(palette)
        sprite.topng('\\'.join(['frame_img', str(sprite.base_tile)]))

def test_totile(testframe, gfxfile):
    sprite = testframe.sprites[0]
    palette = testframe.palettes[sprite.palnum]
    sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)

    base_tiles = sprite.tiles

    sprite.color_tiles(palette)
    assert base_tiles == sprite.totile()

# @pytest.fixture(scope='session')
# @pytest.mark.skip
def test_from_image(tmpdir_factory, testframe, gfxfile):
    for sprite in testframe.sprites:
        palette = testframe.palettes[sprite.palnum]
        sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)
        sprite.color_tiles(palette)
        base = tmpdir_factory.mktemp('data')
        fn = base.join('spritetestpng')
        sprite.topng(str(fn))

        fn2 = base.join('spritetestpng.png')
        test_sprite = Sprite.from_image(str(fn2), sprite)

        for tile1, tile2 in zip(sprite.tiles, test_sprite.tiles):
            assert tile1 == tile2
