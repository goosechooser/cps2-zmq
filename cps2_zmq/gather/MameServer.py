# pylint: disable=E1101
"""
Contains MameServer, WorkerRepresentative, and ServiceQueue classes.
"""
import sys
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
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
    WPROTOCOL = b'MDPW01'
    msgs_recv = 0

    def __init__(self, front_addr, toworkers):
        loop = IOLoop.instance()
        context = zmq.Context.instance()

        front = context.socket(zmq.ROUTER)
        front.setsockopt(zmq.LINGER, 0)
        back = context.socket(zmq.ROUTER)
        back.setsockopt(zmq.LINGER, 0)

        self.frontstream = ZMQStream(front, loop)
        self.frontstream.on_recv(self.handle_frontend)
        self.frontstream.bind(front_addr)

        self.backstream = ZMQStream(back, loop)
        self.backstream.on_recv(self.handle_backend)
        self.backstream.bind(toworkers)

        self.workers = {}
        self.services = {}
        self.heartbeater = None

    def setup(self):
        """
        Sets up the heartbeater callback.
        """
        self.heartbeater = PeriodicCallback(self.beat, HB_INTERVAL)
        self.heartbeater.start()

    def shutdown(self):
        """
        Closes all associated zmq sockets and streams.
        """
        if self.frontstream:
            self.frontstream.socket.close()
            self.frontstream.close()
            self.frontstream = None

        if self.backstream:
            self.backstream.socket.close()
            self.backstream.close()
            self.backstream = None

        if self.heartbeater:
            self.heartbeater.stop()
            self.heartbeater = None

        self.workers = {}
        self.services = {}

    def start(self):
        """
        Start the server
        """
        print('SERVER Starting')
        sys.stdout.flush()
        self.setup()
        IOLoop.instance().start()

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
        """
        Registers any worker who sends a READY message.
        Allows the broker to keep track of heartbeats.

        Args:
            idn (bytes): the id of the worker.
            service (byte-string): the service the work does work for.
        """
        print(self.__class__.__name__, 'Registering worker', idn)
        sys.stdout.flush()

        if idn not in self.workers:
            self.workers[idn] = WorkerRepresentative(self.WPROTOCOL, idn, service, self.backstream)

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
        """
        Unregisters a worker from the server.

        Args:
            idn (bytes): the id of the worker
        """
        print(self.__class__.__name__, 'Unregistering worker', idn)
        sys.stdout.flush()
        self.workers[idn].shutdown()

        service = self.workers[idn].service
        if service in self.services:
            wq, wr = self.services[service]
            wq.remove(idn)

        del self.workers[idn]

    def disconnect_worker(self, idn, socket):
        """
        Tells worker to disconnect from the server, then unregisters the worker.

        Args:
            idn (bytes): id of the worker
            socket (zmq.socket): which socket to send the message out from
        """
        try:
            socket.send_multipart([idn, b'', self.WPROTOCOL, mdp.DISCONNECT])
        except TypeError as err:
            print(self.__class__.__name__, 'encountered', err)
            sys.stdout.flush()
        self.unregister_worker(idn)

    def handle_frontend(self, msg):
        """
        Callback. Handles messages received from clients.
        """
        client_addr = msg.pop(0)
        empty = msg.pop(0)
        protocol = msg.pop(0)
        service = msg.pop(0)
        request = msg[0]

        if service == b'disconnect':
            # Need to determine how many packets are lost doing this.
            print('Client closing. Server disconnecting workers')
            for w in list(self.workers):
                self.disconnect_worker(w, self.backstream.socket)
            IOLoop.instance().stop()

        else:
            self.msgs_recv += 1
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
        """
        Callback. Handles messages received from workers.
        """
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
        """
        Helper function. Formats and sends a request.

        Args:
            socket (zmq.socket): socket to send message out from
            idn (bytes): id of worker to label message with
            client_addr (bytes): addr of client requesting the work
            msg (list): the message to be processed
        """
        request_msg = [idn, b'', self.WPROTOCOL, mdp.REQUEST, client_addr, b'', msg]
        socket.send_multipart(request_msg)

class WorkerRepresentative(object):
    """
    Represents a worker connected to the server.
    Handles heartbeats between the server and a specific worker.
    """
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
        """
        Callback. Periodically sends a heartbeat message to associated worker.
        """
        self.current_liveness -= 1
        self.stream.send_multipart([self.idn, b'', self.protocol, mdp.HEARTBEAT])

    def recv_heartbeat(self):
        """
        Refreshes current_liveness when a heartbeat message is received from associated worker.
        """
        self.current_liveness = HB_LIVENESS

    def is_alive(self):
        """
        Helper function.

        Returns:
            False if current_liveness is under 0, True otherwise
        """
        return self.current_liveness > 0

    def shutdown(self):
        """
        Cleans up!
        """
        self.heartbeater.stop()
        self.heartbeater = None
        self.stream = None

class ServiceQueue(object):
    """
    Its a queue.
    """
    def __init__(self):
        self.q = []

    def __contains__(self, idn):
        return idn in self.queue

    def __len__(self):
        return len(self.q)

    def remove(self, idn):
        """
        Removes from the queue.
        """
        try:
            self.q.remove(idn)
        except ValueError:
            pass

    def put(self, idn):
        """
        Put something in the queue.
        """
        if idn not in self.q:
            self.q.append(idn)

    def get(self):
        """
        Get something from the queue.
        """
        if not self.q:
            return None
        return self.q.pop(0)

if __name__ == '__main__':
    server = MameServer("tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557")
    server.start()
    server.shutdown()
