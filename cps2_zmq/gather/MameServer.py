# pylint: disable=E1101

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream
import msgpack
from cps2_zmq.gather.MameSink import MameSink

class MameServer(object):
    """
    Write some dope stuff here.

    Attributes:
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        addr (str): the address where messages are received at.
        port (str): the port, used with address.
        serversub (:obj:`zmq.Context.socket`): A zmq socket set to SUB.\
        Any messages related to MameWorker status are sent out from here.
        toworkers (str): the address to push work out
        workpusher (:obj:`zmq.Context.socket`): A zmq socket set to PUSH.
        worksink (:obj:`Thread`): a sink for processed messages.
        working (bool): Used in the main loop.
    """
    def __init__(self, port, toworkers, context=None):
        self._loop = IOLoop.instance()
        self._context = context or zmq.Context.instance()
        self._addr = "tcp://localhost"
        self._startport = port

        self._serversub = self._context.socket(zmq.SUB)
        self._serversub.connect(':'.join([self._addr, str(self._startport)]))
        self._serversub.setsockopt_string(zmq.SUBSCRIBE, '')

        self._stream = ZMQStream(self._serversub)
        self._stream.on_recv(self.handle_message)

        self._workpusher = self._context.socket(zmq.PUSH)
        self._workpusher.bind(toworkers)

        self._worksink = None
        self.msgs_recv = 0

    @property
    def worksink(self):
        return self._worksink

    @worksink.setter
    def worksink(self, o):
        if not isinstance(o, MameSink):
            raise TypeError("worksink must be a MameSink")
        self._worksink = o

    def cleanup(self):
        """
        Closes all associated zmq ports.
        """
        self._serversub.close()
        self._workpusher.close()
        self._stream.close()

    def start(self):
        """
        Start. Everything.
        """
        print('starting')
        if self.worksink:
            self._worksink.start()

        self._loop.start()

        # while self._working:
        #     #receive from server/MAME
        #     message = self._serversub.recv()
        #     message = msgpack.unpackb(message, encoding='utf-8')

        #     message = self.process_message(message)
        #     self._workpusher.send(message)

        print("Client Received", self.msgs_recv, "messages")

        if self._worksink:
            self._worksink.join()
            print('sink has joined')
        print('done')

    def handle_message(self, msg):
        """
        Callback. Just unpacks the message and pushes it to workers.
        """
        self.msgs_recv += 1
        msg = msgpack.unpackb(msg[0], encoding='utf-8')

        if msg['frame_number'] == 'closing':
            self._loop.stop()

        self._workpusher.send_json(msg)
