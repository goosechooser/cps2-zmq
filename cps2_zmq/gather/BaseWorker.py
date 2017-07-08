# pylint: disable=E1101
"""
BaseWorker.py
"""

import sys
# from threading import Thread
import msgpack
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import IOLoop, DelayedCallback, PeriodicCallback
from cps2_zmq.gather import mdp

class BaseWorker(object):
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
    HB_INTERVAL = 1000
    HB_LIVENESS = 3

    def __init__(self, idn, front_addr, context=None):
        # super(BaseWorker, self).__init__()
        # self.loop = IOLoop.instance()
        self.idn = bytes(idn, encoding='UTF-8')
        self.front_addr = front_addr
        self.context = context or zmq.Context.instance()
        self.front = self.context.socket(zmq.DEALER)
        self.front.setsockopt(zmq.IDENTITY, self.idn)
        self.frontstream = None
        self.msgs_recv = 0
        self.heartbeater = None
        self.current_liveness = 3
        self._protocol = b'MDPW01'
        self.setup()

    def setup(self):
        self.front.connect(self.front_addr)
        
        self.frontstream = ZMQStream(self.front)
        self.frontstream.on_recv(self.handle_message)
        
        self.heartbeater = PeriodicCallback(self.beat, self.HB_INTERVAL)
        self.ready(self.frontstream, self.idn)
        self.heartbeater.start()
        
    def close(self):
        """
        Closes all sockets.
        """

        if self.heartbeater:
            self.heartbeater.stop()
            self.heartbeater = None
        
        # if self.frontstream:
        self.front.close()
        self.frontstream.close()
        self.frontstream = None
        
        self.report()

        print('Closing')
        sys.stdout.flush()
    
    def start(self):
        self.loop.start()

    def handle_message(self, msg):
        self.current_liveness = self.HB_LIVENESS
        
        empty = msg.pop(0)
        protocol = msg.pop(0)
        command = msg.pop(0)

        # print('Worker', self.idn, 'got command', command)
        # sys.stdout.flush()

        if command == mdp.DISCONNECT:
            print('Worker', self.idn, 'Closing ig')
            sys.stdout.flush()
            IOLoop.instance().stop()
            
            # self.close()
            # self.report()

        if command == mdp.REQUEST:
            client_addr, _, message = msg
            self.msgs_recv += 1

            try:
                unpacked = msgpack.unpackb(message, encoding='utf-8')
            except msgpack.exceptions.UnpackValueError as err:
                print('Worker ERROR', self.idn, err)
                sys.stdout.flush()
                self.close()
                self.report()

            processed = self.process(unpacked)
            packed = msgpack.packb(processed)
            self.reply(self.frontstream, client_addr, packed)

    def report(self):
        """
        Report stats at the end.
        """
        print(self.__class__.__name__, self.idn, 'received', self.msgs_recv, 'messages')
        sys.stdout.flush() 

    def beat(self):
        self.heartbeat(self.frontstream)

        if self.current_liveness < 0:
            # lost connection logging
            print('Worker', self.idn, 'LOST CONNECTION')
            sys.stdout.flush()
            IOLoop.instance().stop()
            # self.close()
            # self.report()

            # delayed = DelayedCallback(self.setup, 5000)
            # delayed.start()

    def process(self, message):
        """
        Should be overridden.
        """
        return message

    def ready(self, socket, service):
        self.current_liveness = self.HB_LIVENESS
        socket.send_multipart([b'', self._protocol, mdp.READY, service])

    def reply(self, socket, client_addr, message):
        socket.send_multipart([b'', self._protocol, mdp.REPLY, client_addr, b'', message])

    def heartbeat(self, socket):
        self.current_liveness -= 1
        # try:
        socket.send_multipart([b'', self._protocol, mdp.HEARTBEAT])
        # except OSError as err:
        #     print('Shits fucked in worker', self.idn, err)

    def disconnect(self, socket):
        socket.send_multipart([b'', self._protocol, mdp.DISCONNECT])

if __name__ == '__main__':
    worker = BaseWorker(str(1), "tcp://127.0.0.1:5557", zmq.Context())
    # worker.start()
    
    IOLoop.current().start()
    print('whats this')
    worker.close()
    print('whats that')
    IOLoop.instance().close(all_fds=True)
