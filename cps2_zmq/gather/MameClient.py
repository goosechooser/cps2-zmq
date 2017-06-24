# pylint: disable=E1101

import zmq
import msgpack
from cps2_zmq.gather.MameSink import MameSink

class MameClient(object):
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
        self._context = context or zmq.Context.instance()
        self._addr = "tcp://localhost"
        self._startport = port

        self._serversub = self._context.socket(zmq.SUB)
        self._serversub.connect(':'.join([self._addr, str(self._startport)]))
        self._serversub.setsockopt_string(zmq.SUBSCRIBE, '')

        self._workpusher = self._context.socket(zmq.PUSH)
        self._workpusher.bind(toworkers)

        self._worksink = None
        self._working = True
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

    def start(self):
        """
        Start. Everything.
        """
        print('starting')
        self._worksink.start()

        while self._working:
            #receive from server/MAME
            message = self._serversub.recv()
            message = msgpack.unpackb(message, encoding='utf-8')

            message = self.process_message(message)
            self._workpusher.send(message)

        print(self.msgs_recv, "Client Received")

        self._worksink.join()
        # self._workpusher.close()
        print('sink has joined')
        print('done')

    def process_message(self, message):
        self.msgs_recv += 1

        if message['frame_number'] == 'closing':
            self._working = False

        message = msgpack.packb(message)
        return message
