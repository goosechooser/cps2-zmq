# pylint: disable=E1101
"""
BaseWorker.py
"""

import sys
from threading import Thread
import msgpack
import zmq

class BaseWorker(Thread):
    """
    Base class for workers that processes messages.

    Attributes:
        idn (str): The worker's 'id'. This an address that is appended to the front \
        of messages it sends to the server.
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        The other side of the socket is usually bound by a MameServer.
        loop (IOLoop): 
        socket_addr (str): The address to connect the frontend socket to. This is usually set
        front (:obj:`zmq.Context.socket`): Requests for work are sent out from here. \
        Work is received on here.
        msgs_recv (int): Counts how many messages this worker received
    """
    def __init__(self, idn, front_addr, context=None):
        super(BaseWorker, self).__init__()
        self.idn = bytes(idn, encoding='UTF-8')
        self.context = context or zmq.Context.instance()

        self.front = self.context.socket(zmq.DEALER)
        self.front.setsockopt(zmq.IDENTITY, self.idn)
        self.front.connect(front_addr)

        self.msgs_recv = 0

    def close(self):
        """
        Closes all sockets.
        """
        self.front.close()

    def run(self):
        working = True

        while working:
            self.front.send_multipart([b'empty', b'ready'])

            _, message = self.front.recv_multipart()

            if message == b'END':
                working = False
                self.front.send_multipart([b'empty', message])
            else:
                self.msgs_recv += 1
                unpacked = msgpack.unpackb(message, encoding='utf-8')
                self.process(unpacked)

        self.close()
        self.report()

    def report(self):
        """
        Report stats at the end.
        """
        print(self.__class__.__name__, self.idn, 'received', self.msgs_recv, 'messages')
        sys.stdout.flush() 


    def process(self, message):
        """
        Should be overridden.
        """
        return message


