# pylint: disable=E1101

import random
from threading import Thread
import zmq
from cps2_zmq.process import Sprite, Frame

def sprite_mask(byte_data):
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
    dict_['pal_number'] = "{0:x}".format(byte_data[3] & 0x001F)
    # dict_['mem_addr'] = "{0:x}".format(byte_data[4])

    return dict_

def mask_all(sprites):
    masked = [sprite_mask(v) for k, v in sprites.items() if all(v)]
    return masked

class Worker(Thread):
    def __init__(self, pullfrom, context=None):
        super(Worker, self).__init__()
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
        self._msgs_recv = 0
        # print('thread setup')
        #add sub socket for kill signal

    def run(self):
        while self._state == 'working':
            polled = dict(self._poller.poll())

            if polled.get(self._puller) == zmq.POLLIN:
                message = self._puller.recv_json()
                frame_number = message['frame_number']

                if frame_number == 'closing' or frame_number < 1140:
                    result = frame_number
                else:
                    result = self._work(message)

                self._pusher.send_pyobj(result)

            if polled.get(self._control) == zmq.POLLIN:
                self._state = 'cleanup'

        while self._state == 'cleanup':
            try:
                message = self._puller.recv_json(zmq.NOBLOCK)
            except zmq.Again:
                self._state = 'done'
                self._pusher.send_pyobj("threaddead")
            else:
                result = self._work(message)
                self._pusher.send_pyobj(result)

        self._cleanup()

    def _work(self, message):
        result = message['frame_number']
        if message['frame_number'] != 'closing':
            if message['frame_number'] > 1140:
                masked = mask_all(message['sprites'])
                palettes = message['palettes']

                sprites = [Sprite.fromdict(m) for m in masked]

                frame = Frame.new(message['frame_number'], sprites, palettes)
                frame.tofile("frame_data\\")
                # frame.topng('_'.join(["frame_img\\frame", str(frame.fnumber)]))
            else:
                result = {}
        else:
            pass

        return result

    def _cleanup(self):
        self._pusher.close()
        self._control.close()

class WorkSink(Thread):
    def __init__(self, nworkers, context=None):
        super(WorkSink, self).__init__()
        self._context = context or zmq.Context.instance()
        self._puller = self._context.socket(zmq.PULL)
        self._puller.bind("inproc://fromworkers")
        self._puller.setsockopt(zmq.LINGER, 0)

        self._workerpub = self._context.socket(zmq.PUB)
        self._workerpub.bind("inproc://control")

        self._nworkers = nworkers
        self._workers = []
        self.daemon = True
        self._msgsrecv = 0

    def _cleanup(self):
        self._puller.close()
        self._workerpub.close()

    def setup_workers(self, pullfrom):
        print('Sink - setup workers')
        self._workers = [Worker(pullfrom) for _ in range(self._nworkers)]

    def run(self):
        print("work sink starting threads")
        for worker in self._workers:
            worker.daemon = True
            worker.start()

        workers_dead = 0
        # while self._working:
        while workers_dead != self._nworkers:
            message = self._puller.recv_pyobj()

            if message == 'closing':
                print('worksink closing')
                self._workerpub.send_string('KILL')
            elif message == 'threaddead':
                workers_dead += 1
            else:
                self._msgsrecv += 1

        # while workers_dead != self._nworkers:
            # message = self._puller.recv_pyobj()
        print('worksink closed')
        self._cleanup()
        print("Received", self._msgsrecv, "messages. Ending.")
