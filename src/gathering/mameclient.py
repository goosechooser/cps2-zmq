# pylint: disable=E1101

import zmq
from src.gathering.mamesink import WorkSink


class MameClient():
    def __init__(self, port, context=None):
        self._context = context or zmq.Context.instance()
        self._addr = "tcp://localhost"
        self._startport = port

        self._serversub = self._context.socket(zmq.SUB)
        self._serversub.connect(':'.join([self._addr, str(self._startport)]))
        self._serversub.setsockopt_string(zmq.SUBSCRIBE, '')

        self._workpusher = self._context.socket(zmq.PUSH)
        self._worksink = None
        self._working = True

    def setup_worksink(self, fromclient, nworkers):
        #set up and start work sink
        print('set up work sink')
        self._workpusher.bind(fromclient)
        self._worksink = WorkSink(nworkers)
        self._worksink.setup_workers(fromclient)

    def start(self):
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
    startpoint = "inproc://toworkers"

    client = MameClient(5556)
    client.setup_worksink(startpoint, num_workers)
    client.start()

if __name__ == '__main__':
    main()
