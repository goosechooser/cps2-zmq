"""
Unit tests for MameWorker.py
"""
import time
import pytest
from cps2_zmq.gather import MameWorker

@pytest.fixture(scope="function")
def test_worker():
    worker = MameWorker.MameWorker("1", "inproc://toworkers", fct=print)
    yield worker
    worker.cleanup()

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
    result = MameWorker._process_message(message)
    print(result)
    assert result[0] == expected

@pytest.mark.parametrize("message, expected", [
    ({'frame_number': 0, 'sprites': [], 'palettes': []}, 0),
    ({'frame_number': 'closing', 'sprites': [], 'palettes': []}, 'closing'),
])
def test_work(message, expected):
    """
    Not sure this test/method is useful anymore.
    If I can figure out the root cause of why json errors
    were being thrown in the first place, I can get rid of them.
    """
    result = MameWorker._work(message)
    assert result == expected
