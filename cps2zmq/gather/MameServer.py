# pylint: disable=E1101
"""
MameServer.py
"""
from zmq.eventloop.ioloop import PeriodicCallback
from cps2zmq.gather import Broker

HB_INTERVAL = 1000
HB_LIVENESS = 3

class MameServer(Broker):
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

    def __init__(self, front_addr, toworkers, log_to_file=False):
        super(MameServer, self).__init__(front_addr, toworkers, log_to_file)
        self.msgreport = None

    def setup(self):
        """
        Sets up msgreport callback.
        """
        super(MameServer, self).setup()
        self.msgreport = PeriodicCallback(self.report, 10 * HB_INTERVAL)
        self.msgreport.start()

    def shutdown(self):
        """
        Closes all associated zmq sockets and streams.
        """
        super(MameServer, self).shutdown()

        if self.msgreport:
            self.msgreport.stop()
            self.msgreport = None

if __name__ == '__main__':
    server = MameServer("tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557")
    server.start()
    server.report()
    server.shutdown()
