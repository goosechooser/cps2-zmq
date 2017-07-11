# pylint: disable=E1101

import time
import sys
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import IOLoop, DelayedCallback, PeriodicCallback
from cps2_zmq.gather import mdp

HB_INTERVAL = 1000
HB_LIVENESS = 3


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
    WORKER_PROTOCOL = b'MDPW01'

    def __init__(self, front_addr, toworkers):
        self.loop = IOLoop.instance()
        self.context = zmq.Context.instance()

        self.frontend = self.context.socket(zmq.ROUTER)

        self.frontstream = ZMQStream(self.frontend)
        self.frontstream.on_recv(self.handle_frontend)
        self.frontstream.bind(front_addr)

        self.backend = self.context.socket(zmq.ROUTER)

        self.backstream = ZMQStream(self.backend)
        self.backstream.on_recv(self.handle_backend)
        self.backstream.bind(toworkers)

        self.msgs_recv = 0
        self.workers = {}
        self.services = {}
        self.heartbeater = None

    def setup(self):
        self.heartbeater = PeriodicCallback(self.beat, HB_INTERVAL)
        self.heartbeater.start()

    def shutdown(self):
        """
        Closes all associated zmq sockets and streams.
        """
        self.frontstream.socket.setsockopt(zmq.LINGER, 0)
        self.frontstream.on_recv(None)
        if self.frontend:
            self.frontend.close()
            self.frontend = None

        if self.frontstream:
            self.frontstream.close()
            self.frontstream = None

        self.backstream.socket.setsockopt(zmq.LINGER, 0)
        self.backstream.on_recv(None)
        if self.backend:
            self.backend.close()
            self.backend = None

        if self.backstream:
            self.backstream.close()
            self.backstream = None

        if self.heartbeater:
            self.heartbeater.stop()
            self.heartbeater = None

        self.workers = {}
        self.services = {}
        self.loop.stop()


    def start(self):
        """
        Start the server
        """
        print('SERVER Starting')
        sys.stdout.flush()
        self.setup()
        self.loop.start()

        print('Workers have joined')
        sys.stdout.flush()

        print("Server Received", self.msgs_recv, "messages")

    def beat(self):
        """
        Checks for dead workers and removes them.
        """
        for w in list(self.workers.values()):
            if not w.is_alive():
                self.unregister_worker(w.idn)

    def register_worker(self, idn, service):
        print('Registering worker', idn)
        sys.stdout.flush()

        if idn not in self.workers:
            self.workers[idn] = WorkerRepresentative(self.WORKER_PROTOCOL, idn, service, self.backstream)

            if service in self.services:
                print(service, 'in self.services')
                sys.stdout.flush()
                wq, wr = self.services[service]
                wq.put(idn)
            else:
                print(service, 'not in self.services')
                sys.stdout.flush()
                q = ServiceQueue()
                q.put(idn)
                self.services[service] = (q, [])

    def unregister_worker(self, idn):
        print('Unregistering worker', idn)
        sys.stdout.flush()
        self.workers[idn].shutdown()

        service = self.workers[idn].service
        if service in self.services:
            wq, wr = self.services[service]
            wq.remove(idn)

        del self.workers[idn]

    def disconnect_worker(self, idn, socket):
        try:
            socket.send_multipart([idn, b'', self.WORKER_PROTOCOL, mdp.DISCONNECT])
        except TypeError as err:
            print(self.__class__.__name__, 'encountered', err)
            sys.stdout.flush()
        self.unregister_worker(idn)

    def handle_frontend(self, msg):
        client_addr = msg.pop(0)
        empty = msg.pop(0)
        protocol = msg.pop(0)
        service = msg.pop(0)
        request = msg[0]
        self.msgs_recv += 1

        if service == b'disconnect':
            print('Client closing. Server disconnecting workers')
            for w in list(self.workers):
                self.disconnect_worker(w, self.backend)
            self.loop.stop()

        else:
            try:
                wq, wr = self.services[service]
                idn = wq.get()

                if idn:
                    self.send_request(self.backstream, idn, client_addr, request)
                else:
                    wr.append(request)

            except KeyError:
                print('Received', service)
                sys.stdout.flush()

    def handle_backend(self, msg):
        worker_idn = msg.pop(0)
        empty = msg.pop(0)
        protocol = msg.pop(0)
        command = msg.pop(0)

        if command == mdp.READY:
            self.register_worker(worker_idn, msg.pop())

        elif command == mdp.REPLY:
            client_addr, _, message = msg
            service = self.workers[worker_idn].service
            try:
                wq, wr = self.services[service]
                # send it wherever
                wq.put(worker_idn)
                if wr:
                    msg = wr.pop(0)
                    self.send_request(self.backstream, worker_idn, client_addr, msg)

            except KeyError:
                print('Received', service)
                sys.stdout.flush()

        elif command == mdp.HEARTBEAT:
            worker = self.workers[worker_idn]
            if worker.is_alive():
                worker.recv_heartbeat()

        elif command == mdp.DISCONNECT:
            self.unregister_worker(worker_idn)

        else:
            self.disconnect_worker(worker_idn, self.backstream)

    def send_request(self, socket, idn, client_addr, msg):
        socket.send_multipart([idn, b'', self.WORKER_PROTOCOL, mdp.REQUEST, client_addr, b'', msg])

class WorkerRepresentative(object):
    def __init__(self, protocol, idn, service, stream):
        self.protocol = protocol
        self.idn = idn
        self.service = service
        self.current_liveness = HB_LIVENESS
        self.stream = stream
        self.last_heartbeat = 0
        self.heartbeater = PeriodicCallback(self.heartbeat, HB_INTERVAL)
        self.heartbeater.start()

    def heartbeat(self):
        self.current_liveness -= 1
        self.stream.send_multipart([self.idn, b'', self.protocol, mdp.HEARTBEAT])

    def recv_heartbeat(self):
        self.current_liveness = HB_LIVENESS

    def is_alive(self):
        return self.current_liveness > 0

    def shutdown(self):
        self.heartbeater.stop()
        self.heartbeater = None
        self.stream = None

class ServiceQueue(object):
    def __init__(self):
        self.q = []

    def __contains__(self, idn):
        return idn in self.queue

    def __len__(self):
        return len(self.q)

    def remove(self, idn):
        try:
            self.q.remove(idn)
        except ValueError:
            pass

    def put(self, idn, *args, **kwargs):
        if idn not in self.q:
            self.q.append(idn)

    def get(self):
        if not self.q:
            return None
        return self.q.pop(0)


if __name__ == '__main__':
    from cps2_zmq.gather.MameWorker import MameWorker
    from cps2_zmq.gather.BaseWorker import BaseWorker

    # front_addr = ':'.join(["tcp://127.0.0.1:5556", str(5556)])
    server = MameServer("tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557")
    num = 1
    workers = [MameWorker(str(num), "tcp://127.0.0.1:5557", b'mame')] # for num in range(1)]
    for w in workers:
        w.start()

    server.start()
    server.shutdown()
