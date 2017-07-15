# pylint: disable=E1101
"""
BaseWorker.py
"""

import sys
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
    msgs_recv = 0

    def __init__(self, idn, front_addr, service):
        self.idn = bytes(idn, encoding='UTF-8')
        self.service = service
        self.front_addr = front_addr
        self.frontstream = None
        self.heartbeater = None
        self.current_liveness = 3
        self._protocol = b'MDPW01'

        self.setup()

    def setup(self):
        """
        Sets up the stream and the heartbeat callback.
        """
        print(self.__class__.__name__, self.idn, 'setting up')
        sys.stdout.flush()

        context = zmq.Context.instance()
        front = context.socket(zmq.DEALER)
        front.setsockopt(zmq.IDENTITY, self.idn)
        front.setsockopt(zmq.LINGER, 0)
        self.frontstream = ZMQStream(front, IOLoop.instance())
        self.frontstream.on_recv(self.handle_message)
        self.frontstream.connect(self.front_addr)

        self.heartbeater = PeriodicCallback(self.beat, self.HB_INTERVAL)
        self.ready(self.frontstream, self.service)
        self.heartbeater.start()

    def close(self):
        """
        Closes all sockets and the heartbeat callback.
        """
        print(self.__class__.__name__, self.idn, 'closing')
        sys.stdout.flush()

        if self.heartbeater:
            self.heartbeater.stop()
            self.heartbeater = None

        if self.frontstream:
            self.frontstream.socket.close()
            self.frontstream.close()
            self.frontstream = None

    def start(self):
        """
        Starts the worker.
        """
        print(self.__class__.__name__, self.idn, 'starting')
        sys.stdout.flush()
        IOLoop.instance().start()

    def handle_message(self, msg):
        """
        A callback. Handles message when it is received.
        """
        self.current_liveness = self.HB_LIVENESS

        empty = msg.pop(0)
        protocol = msg.pop(0)
        command = msg.pop(0)

        if command == mdp.DISCONNECT:
            print(self.__class__.__name__, self.idn,'received disconnect command')
            sys.stdout.flush()
            IOLoop.instance().stop()
            # self.close()

        elif command == mdp.REQUEST:
            # print(self.__class__.__name__, self.idn, 'received request command')
            # sys.stdout.flush()
            self.handle_request(msg)

        else:
            # print('Error', self.__class__.__name__, self.idn, 'received', command, 'command')
            # sys.stdout.flush()
            # raise mdp.UnsupportedCommandException(command)
            pass

    def handle_request(self, msg):
        # print(self.__class__.__name__, self.idn, 'received request command')
        # sys.stdout.flush()
        client_addr, _, message = msg
        self.msgs_recv += 1

        try:
            unpacked = msgpack.unpackb(message, encoding='utf-8')
        except msgpack.exceptions.UnpackValueError as err:
            print('Worker ERROR', self.idn, err)
            sys.stdout.flush()
            IOLoop.instance().stop()
            # self.close()

        processed = self.process(unpacked)
        packed = msgpack.packb(processed)

        try:
            self.reply(self.frontstream, client_addr, packed)
        except TypeError as err:
            print(self.__class__.__name__, 'encountered', err)
            sys.stdout.flush()

    def report(self):
        """
        Report stats.
        """
        print(self.__class__.__name__, self.idn, 'received', self.msgs_recv, 'messages')
        sys.stdout.flush()

    def beat(self):
        """
        A callback. Sends heartbeat and checks if worker has lost connection.
        """
        self.heartbeat(self.frontstream)

        if self.current_liveness < 0:
            print(self.__class__.__name__, self.idn, 'lost connection')
            sys.stdout.flush()
            IOLoop.instance().stop()

            # this would reconnect the worker
            # delayed = DelayedCallback(self.setup, 5000)
            # delayed.start()

    def process(self, message):
        """
        Should be overridden.
        """
        return message

    def ready(self, socket, service):
        """
        Helper function. Ready message is sent once upon connection to the server.
        """
        self.current_liveness = self.HB_LIVENESS
        socket.send_multipart([b'', self._protocol, mdp.READY, service])

    def reply(self, socket, client_addr, message):
        """
        Helper function. Sent upon completion of work.
        """
        reply_msg = [b'', self._protocol, mdp.REPLY, client_addr, b'', message]
        socket.send_multipart(reply_msg)

    def heartbeat(self, socket):
        """
        Helper function. Sent periodically.
        """
        self.current_liveness -= 1
        socket.send_multipart([b'', self._protocol, mdp.HEARTBEAT])

    def disconnect(self, socket):
        """
        Helper function.
        """
        socket.send_multipart([b'', self._protocol, mdp.DISCONNECT])

if __name__ == '__main__':
    worker = BaseWorker(str(1), "tcp://127.0.0.1:5557", b'mame')
    worker.start()
    worker.close()
    worker.report()
