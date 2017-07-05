# pylint: disable=E1101
"""
MameWorker.py
"""
import sys
import msgpack
import zmq
from cps2_zmq.gather.BaseWorker import BaseWorker
from cps2_zmq.process import Sprite, Frame

class MameWorker(BaseWorker):
    """
    MameWorker turns data into Frames.

    Attributes:
        w_id (str): The worker's 'id'. This an address that is appended to the front \
        of messages it sends to the server.
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        The other side of the socket is usually bound by a MameServer.
        socket_addr (str): The address to connect the frontend socket to. This is usually set
        frontend (:obj:`zmq.Context.socket`): Socket that connects to the MameServer address. \
        Sends requests for work.
        working (bool): Whether the worker is in its main loop or closing.
    """
    def __init__(self, idn, front_addr, back_addr, context=None):
        super(MameWorker, self).__init__(idn, front_addr, context)

        self.back = self.context.socket(zmq.DEALER)
        self.back.connect(back_addr)

    def close(self):
        """
        Close all sockets.
        """
        super(MameWorker, self).close()
        self.back.close()

    def process(self, message):
        result = process_message(message)
        packed = msgpack.packb(result)
        self.back.send_multipart([b'empty', packed])

def process_message(message):
    masked = [Sprite.sprite_mask(each) for each in message['sprites']]
    palettes = message['palettes']
    frame_number = message['frame_number']
    sprites = [Sprite.from_dict(m) for m in masked]

    result = Frame.new(frame_number, sprites, palettes)
    return result
    