# pylint: disable=E1101
"""
BaseWorker.py
"""
import queue
import logging
import logging.config
import msgpack
import zmq
from zmq.log.handlers import PUBHandler
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import IOLoop, DelayedCallback, PeriodicCallback
from cps2_zmq.gather import mdp, log

# Have to set up log handling to be done in another thread.
# This is because the IOLoop will block, and logs won't print to the console.
# Alternatively, since end goal will be to run workers headless, who needs the console view?

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

    def __init__(self, idn, front_addr, service, pub_addr=None):
        self.idn = bytes(idn, encoding='UTF-8')
        self.service = service
        self.front_addr = front_addr
        self.frontstream = None
        self.heartbeater = None
        self.pub_addr = pub_addr
        self.publish = None
        self.current_liveness = 3
        self.msgs_recv = 0
        self._protocol = b'MDPW01'
        self._logger = None
        self.setup()

    def setup(self):
        """
        Sets up networking and the heartbeat callback.
        """
        self.setup_logging()
        self._logger.info('Setting worker up')

        context = zmq.Context.instance()
        front = context.socket(zmq.DEALER)
        front.setsockopt(zmq.IDENTITY, self.idn)
        front.setsockopt(zmq.LINGER, 0)
        self.frontstream = ZMQStream(front, IOLoop.instance())
        self.frontstream.on_recv(self.handle_message)
        self.frontstream.connect(self.front_addr)

        if self.pub_addr:
            self.publish = context.socket(zmq.PUB)
            self.publish.setsockopt(zmq.LINGER, 0)
            self.publish.connect(self.pub_addr)

            ph = PUBHandler(self.publish)
            name = '.'.join([self.__class__.__name__, str(self.idn, encoding='utf-8')])
            ph.root_topic = name
            ph.setLevel(logging.INFO)
            self._logger.addHandler(ph)

        self.heartbeater = PeriodicCallback(self.beat, self.HB_INTERVAL)
        self.ready(self.frontstream, self.service)
        self.heartbeater.start()

    def setup_logging(self):
        log.configure_worker(self)
        name = '.'.join([self.__class__.__name__, str(self.idn, encoding='utf-8')])
        self._logger = logging.getLogger(name)
        # self._logger.setLevel(logging.DEBUG)

        # q = queue.Queue(-1)
        # qh = logging.handlers.QueueHandler(q)
        # listener = logging.handlers.QueueListener(q, *logging.getLogger().handlers)

        # listener.start()

    def close(self):
        """
        Closes all sockets and the heartbeat callback.
        """
        self._logger.info('Closing')
        # listener.stop()

        if self.publish:
            self.publish.close()
            self.publish = None

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
        self._logger.info('Starting')
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
            self._logger.info('Received disconnect command')
            IOLoop.instance().stop()
            # self.close()

        elif command == mdp.REQUEST:
            self._logger.info('Received request command')
            self.handle_request(msg)

        else:
            # print('Error', self.__class__.__name__, self.idn, 'received', command, 'command')
            # sys.stdout.flush()
            # raise mdp.UnsupportedCommandException(command)
            pass

    def handle_request(self, msg):
        """
        Callback. Handles a work request.
        """
        client_addr, _, message = msg
        self.msgs_recv += 1

        try:
            unpacked = msgpack.unpackb(message, encoding='utf-8')
        except msgpack.exceptions.UnpackValueError:
            self._logger.error('Failed to unpack', exc_info=True)
            IOLoop.instance().stop()

        processed = self.process(unpacked)
        packed = msgpack.packb(processed)

        try:
            self.reply(self.frontstream, client_addr, packed)
        except TypeError:
            self._logger.error('Encountered error', exc_info=True)

    def report(self):
        """
        Report stats.
        """
        self._logger.info('Received %s messages total', self.msgs_recv)

    def beat(self):
        """
        A callback. Sends heartbeat and checks if worker has lost connection.
        """
        self.heartbeat(self.frontstream)

        if self.current_liveness < 0:
            self._logger.warning('Lost connection')
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
        self._logger.debug('Sending ready')
        socket.send_multipart([b'', self._protocol, mdp.READY, service])

    def reply(self, socket, client_addr, message):
        """
        Helper function. Sent upon completion of work.
        """
        reply_msg = [b'', self._protocol, mdp.REPLY, client_addr, b'', message]
        self._logger.debug('Sending reply')
        socket.send_multipart(reply_msg)

    def heartbeat(self, socket):
        """
        Helper function. Sent periodically.
        """
        self.current_liveness -= 1
        # Set up ability to filter this out - Probably set up a different logger?
        self._logger.debug('Sending heartbeat')
        socket.send_multipart([b'', self._protocol, mdp.HEARTBEAT])

    def disconnect(self, socket):
        """
        Helper function.
        """
        self._logger.debug('Sending disconnect')
        socket.send_multipart([b'', self._protocol, mdp.DISCONNECT])

if __name__ == '__main__':
    worker = BaseWorker(str(1), "tcp://127.0.0.1:5557", b'mame', "tcp://127.0.0.1:5558")
    worker.start()
    worker.report()
    worker.close()
