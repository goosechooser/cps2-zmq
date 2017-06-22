import pytest
from cps2_zmq.gather import MameSink

@pytest.mark.parametrize("message, expected",[
    ({'wid': 420, 'message': 'closing'}, 'worksink closing'),
    ({'wid': 420, 'message': 'threaddead'}, '420 is dead'),
    ({'wid': 420, 'message': 'some result'}, 'another message'),
])
def test_process_message(message, expected, worker):
    sink = MameSink.MameSink("inproc://help")
    worker.wid = message['wid']
    sink.setup_workers2([worker])

    result = sink._process_message(message)
    assert result == expected
    sink._cleanup()

# @pytest.mark.parametrize("messages, expected", [
#     ([{'frame_number': 1141, 'sprites': [[420, 69, 300, 1], [1, 1, 1, 1]], 'palettes': [[]]},
#       {'frame_number': 0, 'sprites': [], 'palettes': []}], 1)
# ])
# @pytest.mark.timeout(timeout=10, method='thread')
# def test_run(workers, messages, expected):
#     sink = MameSink.MameSink("inproc://frommockworkers")
#     sink.setup_workers2(workers)
#     pass