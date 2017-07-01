from abc import ABC, abstractmethod
import json
from cps2_zmq.process import encoding
from PIL import Image

class GraphicAsset(ABC):
    def to_json(self):
        return json.dumps(self, cls=encoding.Cps2Encoder)

    @classmethod
    def from_json(cls, dict_):
        return json.loads(dict_, cls=encoding.Cps2Decoder)

    @abstractmethod
    def to_array(self):
        pass

    def to_bmp(self, savepath):
        """
        Creates a .bmp file
        """
        try:
            image = Image.fromarray(self.to_array(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.to_array(), 'P')
        image.save(savepath + ".bmp")

    def to_png(self, savepath):
        """
        Creates a .png file
        """
        try:
            image = Image.fromarray(self.to_array(), 'RGB')
        except ValueError:
            image = Image.fromarray(self.to_array(), 'P')
        image.save(savepath + ".png")
        