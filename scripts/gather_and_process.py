"""
Gathers frame data sent from a MAME process.
Prints out pretty pictures.
"""

from cps2_zmq.gather.MameServer import MameServer
from cps2_zmq.gather.MameWorker import MameWorker

def main():
    num_workers = 2

    server = MameServer(5556, "inproc://toworkers")
    workers = [MameWorker("inproc://toworkers", "inproc://fromworkers", "inproc://control")
               for i in range(num_workers)]
    sink.workers = workers
    server.worksink = sink
    server.start()

if __name__ == '__main__':
    main()
