"""
Unit tests for MameWorker.py
"""
import time
import pytest
from cps2_zmq.gather import MameWorker

@pytest.mark.parametrize("message, expected", [
    ({'frame_number': 1141, 'sprites': [[420, 69, 300, 1], [1, 1, 1, 1]],
    'palettes': {"1": [0x69, 0x420]}}, 1141),
])
def test_process_message(message, expected):
    result = MameWorker.process_message(message)
    print(result)
    assert result.fnumber == expected
