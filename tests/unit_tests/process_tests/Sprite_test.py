import pytest
from cps2_zmq.process import tile_operations, Sprite

# WORKS
# Not a real test though
@pytest.mark.skip
def test_to_png(testframe, gfxmap):
    for i, sprite in enumerate(testframe.sprites):
        palette = testframe.palettes[sprite.palnum]
        testframe.sprites[i].tiles = tile_operations.read_tiles_from_file(gfxmap, sprite.tiles)
        sprite.color_tiles(palette)
        sprite.to_png('\\'.join(['frame_img', str(sprite.base_tile)]))

def test_from_json(testframe):
    sprite = testframe.sprites[0]
    dict_sprite = sprite.to_json()
    assert isinstance(dict_sprite, str)

    sprite = Sprite.Sprite.from_json(dict_sprite)
    assert isinstance(sprite, Sprite.Sprite)

#broken for the same reason ColorTile's 'to_tile' is broken
@pytest.mark.skip
def test_to_tile(testframe, gfxfile):
    sprite = testframe.sprites[0]
    palette = testframe.palettes[sprite.palnum]
    sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)

    base_tiles = sprite.tiles

    sprite.color_tiles(palette)
    assert base_tiles == sprite.to_tile()

# @pytest.fixture(scope='session')
# @pytest.mark.skip
def test_from_image(tmpdir_factory, testframe, gfxfile):
    for sprite in testframe.sprites:
        palette = testframe.palettes[sprite.palnum]
        sprite.tiles = tile_operations.read_tiles_from_file(gfxfile, sprite.tiles)
        sprite.color_tiles(palette)
        base = tmpdir_factory.mktemp('data')
        fn = base.join('spritetestpng')
        sprite.to_png(str(fn))

        fn2 = base.join('spritetestpng.png')
        test_sprite = Sprite.from_image(str(fn2), sprite)

        for tile1, tile2 in zip(sprite.tiles, test_sprite.tiles):
            assert tile1 == tile2


def test_sprite_mask():
    data = [420, 69, 300, 0]
    expected = {'base_tile': '0x012c', 'priority': 0,
                'flips': (0, 0), 'location': (356, 53),
                'size': (1, 1), 'palnum': '0'}
    result = Sprite.sprite_mask(data)
    print('sprite mask result', result)

    assert  result == expected
    