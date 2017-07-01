from abc import ABC, abstractmethod
import json
from cps2_zmq.process import encoding

class GraphicAsset(ABC):
    def to_json(self):
        return json.dumps(self, cls=encoding.Cps2Encoder)

    @classmethod
    def from_json(cls, dict_):
        return json.loads(dict_, cls=encoding.Cps2Decoder)
