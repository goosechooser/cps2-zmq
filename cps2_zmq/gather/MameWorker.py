# pylint: disable=E1101

import sys
# import random
from threading import Thread
import msgpack
import zmq
from cps2_zmq.process import Sprite, Frame

class MameWorker(Thread):
    """
    MameWorker processes messages.

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
    def __init__(self, w_id, socket_addr, context=None):
        super(MameWorker, self).__init__()
        self._w_id = bytes(w_id, encoding='UTF-8')
        self._context = context or zmq.Context.instance()

        self._frontend = self._context.socket(zmq.DEALER)
        self._frontend.setsockopt_string(zmq.IDENTITY, w_id)
        self._frontend.connect(socket_addr)

        self._working = True
        self._msgs_recv = 0

    @property
    def w_id(self):
        """
        Property.

        Returns:
            bytes
        """
        return self._w_id

    @w_id.setter
    def w_id(self, value):
        if isinstance(value, bytes):
            self._w_id = value
        else:
            self._w_id = bytes(value, encoding='UTF-8')
    
    @property
    def msgs_recv(self):
        """
        Property.

        Returns:
            int
        """
        return self._msgs_recv

    def cleanup(self):
        if not self._frontend.closed:
            self._frontend.close()

    def run(self):
        empty = b'empty'
        ready = b'ready'
        end = b'END'

        while self._working:
            self._frontend.send_multipart([empty, ready])

            _, message = self._frontend.recv_multipart()

            if message == end:
                self._working = False
            else:
                self._msgs_recv += 1
                # do things here
                # print('WORKER', self._w_id, 'received', str(message))

        self.cleanup()
        print('WORKER', self._w_id, 'received', self._msgs_recv, 'messages')

def _work(message):
    """
    Checks the frame number and acts accordingly.
    """
    frame_number = message['frame_number']

    if frame_number == 'closing' or frame_number < 1140:
        result = frame_number
    else:
        result = _process_message(message)

    return result

def _process_message(message, logging=False):
    """
    A private method. Where the actual message processing is done.
    """
    masked = Sprite.mask_all(message['sprites'])
    palettes = message['palettes']

    # Consider just writing message + masked sprites to file?
    # or write a new class that does that HMM??
    sprites = [Sprite.from_dict(m) for m in masked]

    if logging:
        _log(message['frame_number'], sprites, palettes)

    result = [message['frame_number'], sprites, palettes]

    return result

def _log(frame_number, sprites, palettes):
    frame = Frame.new(frame_number, sprites, palettes)
    frame.to_file("frame_data\\")
