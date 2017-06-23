# pylint: disable=E1101

import zmq
import msgpack
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
    def __init__(self, port, toworkers, context=None):
        self._context = context or zmq.Context.instance()
        self._addr = "tcp://localhost"
        self._startport = port

        self._serversub = self._context.socket(zmq.SUB)
        self._serversub.connect(':'.join([self._addr, str(self._startport)]))
        self._serversub.setsockopt_string(zmq.SUBSCRIBE, '')

        self._workpusher = self._context.socket(zmq.PUSH)
        self._workpusher.bind(toworkers)
        
        self._worksink = None
        self._working = True

    @property
    def worksink(self):
        return self._worksink

    @worksink.setter
    def worksink(self, o):
        if not isinstance(o, MameSink):
            raise TypeError("worksink must be a MameSink")
        self._worksink = o

    def start(self):
        """
        Start. Everything.
        """
        print('starting')
        self._worksink.start()

        msgs_recv = 0
        while self._working:
            #receive from server/MAME
            message = self._serversub.recv()
            message = msgpack.unpackb(message, encoding='utf-8')
            msgs_recv += 1
            if message['frame_number'] == 'closing':
                self._working = False
                self._serversub.close()

            message = msgpack.packb(message)
            self._workpusher.send(message)

        print(msgs_recv, "Client Received")

        self._worksink.join()
        print('sink has joined')
        print('done')

def main():
    num_workers = 8

    client = MameClient(5556, "inproc://toworkers")
    workers = [MameWorker("inproc://toworkers", "inproc://fromworkers", "inproc://control")
               for i in range(num_workers)]
    sink = MameSink("inproc://fromworkers", "inproc://control")
    sink.workers = workers
    client.setup_worksink(sink)
    client.start()

if __name__ == '__main__':
    main()
