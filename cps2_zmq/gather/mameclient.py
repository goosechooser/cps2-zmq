# pylint: disable=E1101

import zmq
from cps2_zmq.gather.MameSink import MameSink
from cps2_zmq.gather.MameWorker import MameWorker


class MameClient():
    """
    Write some dope stuff here.
    
    Attributes:
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        addr (str): the address where messages are received at.
        port (str): the port, used with address.
        serversub (:obj:`zmq.Context.socket`): A zmq socket set to SUB.\
        Any messages related to MameWorker status are sent out from here.
        toworkers (str): the address to push work out
        workers (:obj:`list`): A list containing the MameWorkers.
        workpusher (:obj:`zmq.Context.socket`): A zmq socket set to PUSH.
        worksink (:obj:`Thread`): a sink for processed messages.
        working (bool): Used in the main loop.
    """
    def __init__(self, port, context=None):
        self._context = context or zmq.Context.instance()
        self._addr = "tcp://localhost"
        self._startport = port

        self._serversub = self._context.socket(zmq.SUB)
        self._serversub.connect(':'.join([self._addr, str(self._startport)]))
        self._serversub.setsockopt_string(zmq.SUBSCRIBE, '')

        self._toworkers = "inproc://toworkers"
        self._workpusher = self._context.socket(zmq.PUSH)
        self._worksink = None
        self._working = True

    def setup_worksink(self, sink, worker, nworkers):
        """
        Set up the Sink.

        Args:
            sink (:obj:`Thread`): The sink that will collect all processed messages.
            worker (:obj:`Thread`): Worker to use for processing messages.
            nworkers (int): number of workers to create.
        """
        print('set up work sink')
        self._workpusher.bind(self._toworkers)
        self._worksink = sink
        self._worksink.setup_workers(worker, nworkers, self._toworkers)

    def start(self):
        """
        Start. Everything.
        """
        print('starting')
        self._worksink.start()

        msgs_recv = 0
        while self._working:
            #receive from server/MAME
            message = self._serversub.recv_json()
            msgs_recv += 1
            if message['frame_number'] == 'closing':
                self._working = False
                self._serversub.close()

            self._workpusher.send_json(message)

        print(msgs_recv, "Client Received")

        self._worksink.join()
        print('sink has joined')
        print('done')

def main():
    num_workers = 8

    client = MameClient(5556)
    client.setup_worksink(MameSink(), MameWorker, num_workers)
    client.start()

if __name__ == '__main__':
    main()
