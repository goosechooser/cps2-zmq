# pylint: disable=E1101

import zmq
import pytest
from cps2_zmq.gather.MameServer import MameServer, close_workers

@pytest.fixture(scope="module")
def test_socket():
    context = zmq.Context.instance()
    test_socket = context.socket(zmq.DEALER)
    test_socket.bind("inproc://testsocket")
    yield test_socket
    test_socket.close()

@pytest.mark.timeout(timeout=10, method='thread')
def test_close_workers(worker, test_socket):
    worker.idn = bytes('1', encoding='UTF-8')
    workers = [worker]

    for w in workers:
        w.frontend.connect("inproc://testsocket")

    close_workers(workers, test_socket)
    for w in workers:
        assert w.frontend.recv_multipart()
