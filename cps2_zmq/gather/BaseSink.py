# pylint: disable=E1101
"""
BaseSink.py
"""

import sys
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import IOLoop
from cps2_zmq.gather.BaseWorker import BaseWorker
from cps2_zmq.gather import mdp

class BaseSink(BaseWorker):
    """
    Base class for sinks that will take care of logging-related duties?
    """
    def __init__(self, idn, front_addr, sub_addr, topics):
        self.sub_addr = sub_addr
        self.substream = None
        self.topics = topics
        super(BaseSink, self).__init__(idn, front_addr, b'sink')

    def setup(self):
        super(BaseSink, self).setup()
        context = zmq.Context.instance()
        sub = context.socket(zmq.SUB)

        for topic in self.topics:
            sub.setsockopt_string(zmq.SUBSCRIBE, topic)

        self.substream = ZMQStream(sub, IOLoop.instance())
        self.substream.on_recv(self.handle_pub)
        self.substream.bind(self.sub_addr)

    def close(self):
        """
        Closes all sockets and the heartbeat callback.
        """
        super(BaseSink, self).close()
        if self.substream:
            self.substream.socket.close()
            self.substream.close()
            self.substream = None

    def handle_message(self, msg):
        """
        A callback. Should only handle disconnect.
        """
        self.current_liveness = self.HB_LIVENESS

        empty = msg.pop(0)
        protocol = msg.pop(0)
        command = msg.pop(0)

        if command == mdp.DISCONNECT:
            print(self.__class__.__name__, self.idn, 'received disconnect command')
            sys.stdout.flush()
            IOLoop.instance().stop()

        else:
            pass
            # print('Error', self.__class__.__name__, self.idn, 'received', command, 'command')
            # sys.stdout.flush()
            # raise mdp.UnsupportedCommandException(command)

    def handle_pub(self, msg):
        """
        Figure out extent to which this'll be overridden.
        """
        self.msgs_recv += 1
        print(msg)
        sys.stdout.flush()

        topic = msg.pop(0)
        message = msg.pop()

        self.process_pub(message)

    def process_pub(self, msg):
        """
        Should be overridden.
        """
        print(msg)
        return msg

if __name__ == '__main__':
    sink = BaseSink("1", "tcp://127.0.0.1:5557", "tcp://127.0.0.1:5558", [''])
    sink.start()
    sink.close()
