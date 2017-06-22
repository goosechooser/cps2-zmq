# pylint: disable=E1101

from threading import Thread
import zmq

class MameSink(Thread):
    """
    MameSink is the final point in the message processing chain.\
    Functionality related to further processing of collected messages would be held here.\
    It is also responsible for creating and cleaning up Worker threads.

    Attributes:
        context (:obj:`zmq.Context`): required by ZMQ to make the magic happen.
        puller (:obj:`zmq.Context.socket`): The zmq socket where processed messages are pulled from.
        workerpub (:obj:`zmq.Context.socket`): A zmq socket set to PUB.\
        Any messages related to MameWorker status are sent out from here.
        nworkers (int): the number of MameWorkers to create.
        workers (:obj:`list`): A list containing the MameWorkers.
        msgsrecv (int): The number of messages received. Used in debugging/logging.
    """
    def __init__(self, pullfrom, context=None):
        super(MameSink, self).__init__()
        self._context = context or zmq.Context.instance()
        self._puller = self._context.socket(zmq.PULL)
        self._puller.bind(pullfrom)
        self._puller.setsockopt(zmq.LINGER, 0)

        self._workerpub = self._context.socket(zmq.PUB)
        self._workerpub.bind("inproc://control")

        self._nworkers = 0
        self._workers = {}
        self.daemon = True
        self._msgsrecv = 0

    def _cleanup(self):
        self._puller.close()
        self._workerpub.close()

    # Replace worker, nworkers with just a list of workers
    def setup_workers(self, worker, nworkers, pullfrom):
        """
        Sets up all the MameWorker threads

        Args:
            worker (:obj:`Thread`): the class that will do the message processing.
            nworkers (int): how many workers.
            pullfrom (:obj:`zmq.Context.socket`): Where processed messages are pulled from.
        """
        print('Sink - setup workers')
        self._nworkers = nworkers
        self._workers = [worker(pullfrom) for _ in range(self._nworkers)]

    # Does this need to be a method here? 
    def setup_workers2(self, workers):
        self._workers = {worker.wid : worker for worker in workers}

    def run(self):
        """
        MameSink is a subclass of Thread, run is called when the thread started.
        """
        print("work sink starting threads")
        for worker in self._workers:
            worker.daemon = True
            worker.start()

        while self._workers:
            message = self._puller.recv_pyobj()

            self._process_message(message)

        print('worksink closed')
        self._cleanup()
        print("Received", self._msgsrecv, "messages. Ending.")

    def _process_message(self, message):
        if message['message'] == 'closing':
            print('worksink closing')
            self._workerpub.send_string('KILL')
            result = 'worksink closing'

        elif message['message'] == 'threaddead':
            result = ' '.join([str(message['wid']), 'is dead'])
            del self._workers[message['wid']]

        else:
            self._msgsrecv += 1
            # result = self._msgsrecv
            result = 'another message'
        return result



