# pylint: disable=E1101

import sys
# import random
from threading import Thread
import msgpack
import zmq
from cps2_zmq.process import Sprite, Frame

class MameWorker(Thread):
    """
    MameWorker processes messages sent by a MAME process.\

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
        # print('WORKER running')
        # sys.stdout.flush()

        while self._working:
            self._frontend.send_multipart([
                b'empty',
                b'ready'
            ])

            _, message = self._frontend.recv_multipart()
            if message == b'END':
                self._working = False
            else:
                self._msgs_recv += 1
                # print('WORKER', self._w_id, 'received', str(message))
            #     sys.stdout.flush()

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
    masked = mask_all(message['sprites'])
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

# sprites is a list actually
def mask_all(sprites):
    """
    Calls sprite_mask on every value in the sprites dict.

    Args:
        sprites (:obj:`list` of :obj:`list`): the raw sprite data

    Returns:
        a list.
    """
    masked = [sprite_mask(s) for s in sprites if all(s)]
    return masked

def sprite_mask(byte_data):
    """
    Turns the 8 bytes of raw sprite information into something usable.

    Args:
        byte_data (:obj:`list`): a list of 4 uint16 containing all the data for a Sprite.

    Returns:
        a dict. This dict can be used by the Sprite factory method :meth:`fromdict`.
    """
    dict_ = {}
    dict_['priority'] = (byte_data[0] & 0xC000) >> 14
    dict_['x'] = byte_data[0] & 0x03FF
    dict_['y'] = byte_data[1] & 0x03FF
    dict_['eol'] = (byte_data[1] & 0x8000) >> 15
    #hex: {0:x};  oct: {0:o};  bin: {0:b}".format(42)
    top_half = "{0:#x}".format((byte_data[1] & 0x6000) >> 13)
    bottom_half = "{0:x}".format(byte_data[2])
    dict_['tile_number'] = ''.join([top_half, bottom_half])
    dict_['height'] = ((byte_data[3] & 0xF000) >> 12) + 1
    dict_['width'] = ((byte_data[3] & 0x0F00) >> 8) + 1
    #(0= Offset by X:-64,Y:-16, 1= No offset)
    dict_['offset'] = (byte_data[3] & 0x0080) >> 7
    #Y flip, X flip (1= enable, 0= disable)
    dict_['yflip'] = (byte_data[3] & 0x0040) >> 69
    dict_['xflip'] = (byte_data[3] & 0x0020) >> 5
    dict_['pal_number'] = "{0:d}".format(byte_data[3] & 0x001F)
    # dict_['mem_addr'] = "{0:x}".format(byte_data[4])

    return dict_
    