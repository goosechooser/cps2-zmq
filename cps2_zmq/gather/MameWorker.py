# pylint: disable=E1101
"""
MameWorker.py
"""
import random
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

    def __init__(self, idn, front_addr, service, pub_addr=None):
        self.pub_addr = pub_addr
        self.publish = None
        super(MameWorker, self).__init__(idn, front_addr, service)

    def setup(self):
        if self.pub_addr:
            context = zmq.Context.instance()
            self.publish = context.socket(zmq.PUB)
            self.publish.setsockopt(zmq.LINGER, 0)
            self.publish.connect(self.pub_addr)

        super(MameWorker, self).setup()

    def close(self):
        super(MameWorker, self).close()
        if self.publish:
            self.publish.close()
            self.publish = None

    def log_result(self, result):
        """
        Publishes the result.
        """
        if self.publish:
            message = [b'frame', self.idn, msgpack.packb(result)]
            self.publish.send_multipart(message)

    def process(self, message):
        processed = process_message(message)
        json_msg = processed.to_json()
        self.log_result(json_msg)
        return json_msg

def process_message(message):
    """
    Processes raw frame data sent by a MAME instance.
    """
    masked = [Sprite.sprite_mask(each) for each in message['sprites']]
    palettes = message['palettes']
    frame_number = message['frame_number']
    sprites = [Sprite.from_dict(m) for m in masked]
    result = Frame.new(frame_number, sprites, palettes)

    return result


if __name__ == '__main__':
    worker = MameWorker(str(random.randint(69, 420)), "tcp://127.0.0.1:5557", b'mame', pub_addr="tcp://127.0.0.1:5558")
    worker.start()
    worker.report()
