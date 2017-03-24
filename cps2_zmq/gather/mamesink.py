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
    def __init__(self, context=None):
        super(MameSink, self).__init__()
        self._context = context or zmq.Context.instance()
        self._puller = self._context.socket(zmq.PULL)
        self._puller.bind("inproc://fromworkers")
        self._puller.setsockopt(zmq.LINGER, 0)

        self._workerpub = self._context.socket(zmq.PUB)
        self._workerpub.bind("inproc://control")

        self._nworkers = 0
        self._workers = []
        self.daemon = True
        self._msgsrecv = 0

    def _cleanup(self):
        self._puller.close()
        self._workerpub.close()

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

    def run(self):
        """
        MameSink is a subclass of Thread, run is called when the thread started.
        """
        print("work sink starting threads")
        for worker in self._workers:
            worker.daemon = True
            worker.start()

        workers_dead = 0
        while workers_dead != self._nworkers:
            message = self._puller.recv_pyobj()

            if message == 'closing':
                print('worksink closing')
                self._workerpub.send_string('KILL')
            elif message == 'threaddead':
                workers_dead += 1
            else:
                self._msgsrecv += 1

        print('worksink closed')
        self._cleanup()
        print("Received", self._msgsrecv, "messages. Ending.")



