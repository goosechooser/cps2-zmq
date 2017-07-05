# pylint: disable=E1101

import sys
import msgpack
import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream
from cps2_zmq.gather.MameWorker import MameWorker

class MameServer(object):
    """
    MameServer receives messages sent by an instance of MAME, and passes it to workers \
    for processing.

    Attributes:
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        port (str): the port the serversub socket binds to.
        serversub (:obj:`zmq.Context.socket`): A zmq socket set to SUB.\
        MameClients connect and send messages here.
        toworkers (str): the address to push work out on
        backend (:obj:`zmq.Context.socket`): A zmq socket set to ROUTER. \
        Routes work to the worker that requested it.
        backstream (:obj:`zmq.eventloop.zmqstream.ZMQStream`): Used for registering callbacks \
        with the backend socket.
        msgs_recv (int): Total number of messages received.
        workers (list of threads): Pool to keep track of workers.
    """
    def __init__(self, port, toworkers, context=None):
        self.loop = IOLoop.instance()
        self.context = context or zmq.Context.instance()
        self.port = port

        self.front = self.context.socket(zmq.SUB)
        self.front.bind(':'.join(["tcp://127.0.0.1", str(self.port)]))
        self.front.setsockopt_string(zmq.SUBSCRIBE, '')

        self.backend = self.context.socket(zmq.ROUTER)
        self.backend.bind(toworkers)

        self.backstream = ZMQStream(self.backend)
        self.backstream.on_recv(self.handle_router)

        self.msgs_recv = 0
        self.workers = []
        self.working = True

    def cleanup(self):
        """
        Closes all associated zmq sockets and streams.
        """
        self.front.close()
        self.backend.close()
        self.backstream.close()

    def start(self):
        """
        Start the server
        """
        print('SERVER Starting')
        sys.stdout.flush()

        for worker in self.workers:
            worker.start()

        self.loop.start()

        self.cleanup()

        print('Workers have joined')
        sys.stdout.flush()

        print("Server Received", self.msgs_recv, "messages")

    def handle_router(self, msg):
        """
        Callback. Handles replies from workers.
        """
        #Receives req from worker
        worker_addr, empty, worker_msg = msg

        #gets message from client
        if self.working:
            client_message = self.front.recv()
            unpacked = msgpack.unpackb(client_message, encoding='utf-8')
            if unpacked['frame_number'] != 'closing':
                self.msgs_recv += 1
                message = msgpack.packb(unpacked)
                self.backend.send_multipart([worker_addr, empty, message])

            else:
                print('client closing')
                sys.stdout.flush()
                close_workers(self.workers, self.backend)
                self.working = False

        else: 
            if worker_msg == b'END':
                self.workers.pop()

            if not self.workers:
                self.loop.stop()

def close_workers(workers, socket):
    """
    Signals to workers its time to stop.

    Args:
        workers (list): the workers to message
        socket (:obj:`zmq.Context.socket`): the socket to send messages on
    """
    empty = b'empty'
    message = b'END'

    for worker in workers:
        address = worker.idn
        socket.send_multipart([address, empty, message])

if __name__ == '__main__':
    server = MameServer(5556, "inproc://toworkers")
    server.workers = [MameWorker(str(num), "inproc://toworkers", "inproc://none") for num in range(1, 5)]

    server.start()
