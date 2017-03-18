import jsonpickle
from PIL import Image

class Frame(object):
    def __init__(self, fnumber, sprites, palettes):
        self._fnumber = fnumber
        self._palettes = palettes
        self._sprites = sprites

    def __repr__(self):
        return "Frame {} has {} sprites".format(self._fnumber, len(self._sprites))

    @property
    def fnumber(self):
        return self._fnumber

    @property
    def sprites(self):
        return self._sprites

    @property
    def palettes(self):
        return self._palettes

    def add_sprites(self, sprites):
        self._sprites.extend(sprites)

    def topng(self, fname, imsize=(400, 400)):
        canvas = Image.new('RGB', imsize)
        for sprite in self._sprites:
            palette = self._palettes[sprite.palnum]
            # sprite.color_tiles(palette)
            canvas.paste(
                Image.fromarray(sprite.toarray(), 'RGB'),
                sprite.location
                )
        canvas.save('.'.join([fname, 'png']))

    def tofile(self, path):
        file_name = '.'.join([str(self._fnumber), 'json'])
        path = '\\'.join([path, file_name])

        with open(path, 'w') as f:
            f.write(jsonpickle.encode(self))

def new(fnumber, sprites, palettes):
    converted = {}
    for k, v in palettes.items():
        conv = {kk : _argb_to_rgb(hex(color)[2:]) for kk, color in v.items()}
        converted[k] = conv
    return Frame(fnumber, sprites, converted)


def _argb_to_rgb(color):
    """Converts the 2 byte ARGB format the cps2 uses.

    Returns a bytes() of 3 byte RGB.
    """
    if len(color) < 4:
        color = (4 - len(color)) * '0' + color
    return (int(color[1] * 2, 16), int(color[2] * 2, 16), int(color[3] * 2, 16))


def fromfile(path):
    with open(path, 'r') as f:
        frame = jsonpickle.decode(f.read())

    return frame
