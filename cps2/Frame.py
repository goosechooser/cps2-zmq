import jsonpickle
from PIL import Image

class Frame(object):
    def __init__(self, fnumber, sprites, palette):
        self._fnumber = fnumber
        self._palette = palette
        self._sprites = sprites

    def __repr__(self):
        return "Frame {} has {} sprites".format(self._fnumber, len(self._sprites))

    @property
    def fnumber(self):
        return self._fnumber

    @property
    def sprites(self):
        return self._sprites

    def add_sprites(self, sprites):
        self._sprites.extend(sprites)

    def topng(self, fname, imsize=(400, 400)):
        canvas = Image.new('RGB', imsize)
        for sprite in self._sprites:
            palette = self._palette[sprite.palette]
            canvas.paste(
                Image.fromarray(sprite.toarray(palette), 'RGB'),
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
        conv = [_argb_to_rgb(hex(color)[1:]) for color in v]
        converted[k] = conv

    return Frame(fnumber, sprites, converted)


def _argb_to_rgb(color):
    """Converts the 2 byte ARGB format the cps2 uses.

    Returns a bytes() of 3 byte RGB.
    """
    if len(color) < 4:
        color = (4 - len(color)) * '0' + color
    return bytes.fromhex(color[1] * 2 + color[2] * 2 + color[3] * 2)


def fromfile(path):
    with open(path, 'r') as f:
        frame = jsonpickle.decode(f.read())

    return frame
