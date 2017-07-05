"""
Unit tests for MameWorker.py
"""
import time
import pytest
from cps2_zmq.gather import MameWorker

@pytest.fixture(scope="function")
def test_worker():
    worker = MameWorker.MameWorker("1", "inproc://toworkers", "inproc://none")
    yield worker
    worker.close()

@pytest.mark.skip
@pytest.mark.timeout(timeout=10, method='thread')
@pytest.mark.parametrize("messages, expected", [
    (1, 1),
    (10, 10)
])
def test_run(server, test_worker, messages, expected):
    test_worker.start()
    print("Worker started")

    server.make_messages(messages)
    print("Messages made")

    server.start()
    time.sleep(5)
    server.close_workers([test_worker])

    assert test_worker.msgs_recv == expected

@pytest.mark.parametrize("message, expected", [
    ({'frame_number': 1141, 'sprites': [[420, 69, 300, 1], [1, 1, 1, 1]], 'palettes': [[]]}, 1141),
])
def test_process_message(message, expected):
    result = MameWorker.process_message(message)
    assert result.fnumber == expected
