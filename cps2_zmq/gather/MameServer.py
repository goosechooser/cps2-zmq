# pylint: disable=E1101

import msgpack
import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream
from cps2_zmq.gather.MameWorker import MameWorker

class MameServer(object):
    """
    Write some dope stuff here.

    Attributes:
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        addr (str): the address where messages are received at.
        port (str): the port, used with address.
        serversub (:obj:`zmq.Context.socket`): A zmq socket set to SUB.\
        MameClients connect and send messages here.
        toworkers (str): the address  to push work out
        backend (:obj:`zmq.Context.socket`): A zmq socket set to ROUTER. \
        Routes work to the worker that requested it.
        backstream (:obj:`zmq.eventloop.zmqstream.ZMQStream`): Used for registering callbacks \
        with the backend socket.
        msgs_recv (int): Total number of messages received .
    """
    def __init__(self, port, toworkers, context=None):
        self._loop = IOLoop.instance()
        self._context = context or zmq.Context.instance()
        self._addr = "tcp://127.0.0.1"
        self._port = port

        self._serversub = self._context.socket(zmq.SUB)
        self._serversub.bind(':'.join([self._addr, str(self._port)]))
        self._serversub.setsockopt_string(zmq.SUBSCRIBE, '')

        self._backend = self._context.socket(zmq.ROUTER)
        self._backend.bind(toworkers)

        self._backstream = ZMQStream(self._backend)
        self._backstream.on_recv(self.handle_router)

        self.msgs_recv = 0
        self._workers = []

    @property
    def workers(self):
        return self._workers

    @workers.setter
    def workers(self, value):
        self._workers = value

    def cleanup(self):
        """
        Closes all associated zmq ports.
        """
        self._serversub.close()
        self._backend.close()
        self._backstream.close()

    def start(self):
        """
        Start. Everything.
        """
        print('SERVER Starting')

        for worker in self.workers:
            worker.start()

        self._loop.start()

        self.cleanup()

        print('Workers have joined')

        print("Client Received", self.msgs_recv, "messages")

    def handle_router(self, msg):
        """
        Callback. Handles replies from workers.
        """
        #Receives req from worker
        address, empty, ready = msg

        #gets message from client
        sub_message = self._serversub.recv_multipart()
        unpacked = msgpack.unpackb(sub_message[0], encoding='utf-8')

        if unpacked['frame_number'] != 'closing':
            self.msgs_recv += 1

            message = bytes(str(unpacked['frame_number']), encoding='UTF-8')
            self._backend.send_multipart([
                address,
                empty,
                message
            ])
        else:
            close_workers(self._workers, self._backend)
            self._loop.stop()

def close_workers(workers, socket):
    """
    Sends b'END'
    """
    empty = b'empty'
    message = b'END'
    
    for worker in workers:
        address = worker.w_id
        socket.send_multipart([
            address,
            empty,
            message
        ])

if __name__ == '__main__':
    server = MameServer(5556, "inproc://toworkers")
    server.workers = [MameWorker(str(num), "inproc://toworkers") for num in range(1, 3)]

    server.start()
