import mmap
import pytest
import jsonpickle
from cps2 import tile_printer

def get_file(fpath):
    return open(fpath, 'r+b')

def get_frame(framefile):
    with open(framefile, 'r') as f:
        data = f.read()
    return jsonpickle.decode(data)

FRAME = get_frame('frame_data\\1141.json')
GFXFILE = get_file('data\\vm3_combined')
GFXMAP = mmap.mmap(GFXFILE.fileno(), 0)

# should supply a test input + palette and check output
@pytest.mark.skip
def test_colortile():
    sprite = FRAME.sprites[0]
    palette = FRAME.palettes[sprite.palnum]
    sprite.tiles = tile_printer.fill_tiles(GFXFILE, sprite.tiles)
    sprite.color_tiles(palette)

#WORKS
@pytest.mark.skip
def test_topng():
    for i, sprite in enumerate(FRAME.sprites):
        palette = FRAME.palettes[sprite.palnum]
        FRAME.sprites[i].tiles = tile_printer.fill_tiles(GFXMAP, sprite.tiles)
        sprite.color_tiles(palette)
        sprite.topng('\\'.join(['frame_img', str(sprite.base_tile)]))
    FRAME.topng('\\'.join(['frame_img', str(FRAME.fnumber)]))
