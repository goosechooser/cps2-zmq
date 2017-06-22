import pytest
from cps2_zmq.gather import MameSink

@pytest.fixture(scope="function")
def sink():
    sink = MameSink.MameSink("inproc://frommockworkers")
    yield sink
    sink.cleanup()

@pytest.mark.parametrize("message, expected", [
    ({'wid': 420, 'message': 'closing'}, 'worksink closing'),
    ({'wid': 420, 'message': 'threaddead'}, '420 is dead'),
    ({'wid': 420, 'message': 'some result'}, 'another message'),
])
def test_process_message(message, expected, sink, worker):
    worker.wid = message['wid']
    sink.setup_workers2([worker])

    result = sink._process_message(message)
    assert result == expected

def test_run(sink, tworkers):
    # sink = MameSink.MameSink("inproc://frommockworkers")

    messages = ['some result', 'closing', 'threaddead']
    for worker in tworkers:
        worker.messages = [{'wid' : worker.wid, 'message': msg} for msg in messages]
        worker.connect_push("inproc://frommockworkers")

    sink.setup_workers2(tworkers)

    sink.start()
    #block and let the sink run
    sink.join()
    assert not sink.workers
    assert sink._msgsrecv == len(tworkers) * len(messages)
    