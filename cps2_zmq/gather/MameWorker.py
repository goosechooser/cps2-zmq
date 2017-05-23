# pylint: disable=E1101

import random
from threading import Thread
import msgpack
import zmq
from cps2_zmq.process import Sprite, Frame

class MameWorker(Thread):
    """
    MameWorker processes messages sent by a MAME process.\
    MameWorker threads are created by a MameSink and cleaned up by the MameSink.

    Attributes:
        id (int): used for debugging or logging purposes.
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        puller (:obj:`zmq.Context.socket`): A zmq socket set to PULL messages.\
        The other side of the socket is usually bound by a MameClient.
        pusher (:obj:`zmq.Context.socket`): A zmq socket set to PUSH processed messages.\
        The other side is connected to the MameSink
        control (:obj:`zmq.Context.socket`): A zmq socket set to SUB.\
        The only time it receives a message on this socket is when its time to stop working.
        poller (:obj:`zmq.Poller`): Reads from the sockets that receive messages\
        in a non-blocking manner.
        state (str): What the worker is currently doing.\
        Values for this are 'working', 'cleanup', 'closing', and 'done'.
    """
    def __init__(self, pullfrom, context=None):
        super(MameWorker, self).__init__()
        self._id = random.randrange(1, 666)
        self._context = context or zmq.Context.instance()

        self._puller = self._context.socket(zmq.PULL)
        self._puller.connect(pullfrom)
        self._puller.setsockopt(zmq.LINGER, 0)

        self._pusher = self._context.socket(zmq.PUSH)
        self._pusher.connect("inproc://fromworkers")

        self._control = self._context.socket(zmq.SUB)
        self._control.connect("inproc://control")
        self._control.setsockopt_string(zmq.SUBSCRIBE, '')

        self._poller = zmq.Poller()
        self._poller.register(self._puller, zmq.POLLIN)
        self._poller.register(self._control, zmq.POLLIN)

        self._state = 'working'

    def run(self):
        """
        MameWorker is a subclass of Thread, run is called when the thread started.\
        More specifically, anything related to pulling or pushing messages is handled here.
        """
        while self._state == 'working':
            polled = dict(self._poller.poll())

            if polled.get(self._puller) == zmq.POLLIN:
                message = self._puller.recv()
                message = msgpack.unpackb(message, encoding='utf-8')

                result = _process_message(message)

                self._pusher.send_pyobj(result)

            if polled.get(self._control) == zmq.POLLIN:
                self._state = 'cleanup'

        while self._state == 'cleanup':
            try:
                message = self._puller.recv(zmq.NOBLOCK)
                message = msgpack.unpackb(message, encoding='utf-8')
            except zmq.Again:
                self._state = 'done'
                self._pusher.send_pyobj("threaddead")
            else:
                result = _work(message)
                self._pusher.send_pyobj(result)

        self._cleanup()


    def _cleanup(self):
        self._pusher.close()
        self._control.close()

def _process_message(message):
    """
    Checks the frame number and acts accordingly.
    """
    frame_number = message['frame_number']

    if frame_number == 'closing' or frame_number < 1140:
        result = frame_number
    else:
        result = _work(message)
    return result

def _work(message, logging=False):
    """
    A private method. Where the actual message processing is done.
    """
    result = message['frame_number']
    if message['frame_number'] != 'closing':
        if message['frame_number'] > 1140:
            masked = mask_all(message['sprites'])
            palettes = message['palettes']

            # Consider just writing message + masked sprites to file?
            # would decouple MameSink/MameClient from cps2_zmq.process
            sprites = [Sprite.from_dict(m) for m in masked]

            if logging:
                _log(message, sprites, palettes)

        else:
            result = {}
    else:
        pass

    return result

def _log(message, sprites, palettes):
    frame = Frame.new(message['frame_number'], sprites, palettes)
    frame.to_file("frame_data\\")

# sprites is a list actually
def mask_all(sprites):
    """
    Calls sprite_mask on every value in the sprites dict.

    Args:
        sprites (dict): This is a dict because\
        I can't figure out how to have the server send sprite data as a list.\
        Need to recheck this later.

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
    