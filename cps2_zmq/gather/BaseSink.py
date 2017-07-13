# pylint: disable=E1101
"""
BaseSink.py
"""

import sys
import json
import msgpack
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import IOLoop
from cps2_zmq.gather.BaseWorker import BaseWorker
from cps2_zmq.gather import mdp

class BaseSink(BaseWorker):
    """
    Base class for sinks that will take care of logging-related duties?
    """
    def __init__(self, idn, front_addr, service, sub_addr, topics):
        self.sub_addr = sub_addr
        self.substream = None
        self.topics = topics
        super(BaseSink, self).__init__(idn, front_addr, service)

    def setup(self):
        super(BaseSink, self).setup()
        context = zmq.Context.instance()
        sub = context.socket(zmq.SUB)
        sub.setsockopt_string(zmq.SUBSCRIBE, self.topics)
        sub.setsockopt(zmq.LINGER, 0)
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
        empty = msg.pop(0)
        protocol = msg.pop(0)
        command = msg.pop(0)

        if command == mdp.DISCONNECT:
            print(self.__class__.__name__, self.idn, 'received disconnect command')
            sys.stdout.flush()
            IOLoop.instance().stop()

        else:
            print('Error', self.__class__.__name__, self.idn, 'received', command, 'command')
            sys.stdout.flush()
            raise mdp.UnsupportedCommandException(command)

    def handle_pub(self, msg):
        """
        Figure out extent to which this'll be overridden.
        """
        self.msgs_recv += 1
        topic = msg.pop(0)
        pub_addr = msg.pop(0)
        message = msg.pop()

        try:
            unpacked = msgpack.unpackb(message, encoding='utf-8')
        except msgpack.exceptions.UnpackValueError as err:
            print(self.__class__.__name__, self.idn, err)
            sys.stdout.flush()
        else:
            self.process_pub(unpacked)

    def process_pub(self, msg):
        """
        Should be overridden.
        """
        return msg

if __name__ == '__main__':
    sink = BaseSink("sink-1", "tcp://127.0.0.1:5557", 'logging', "inproc://none", "ok")
    sink.close()
