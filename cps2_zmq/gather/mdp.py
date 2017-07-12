"""
Constants used by brokers, workers, and clients implementing the Majordomo protocol.
More information can be found at: https://rfc.zeromq.org/spec:7/MDP/
"""
READY = b'\x01'
REQUEST = b'\x02'
REPLY = b'\x03'
HEARTBEAT = b'\x04'
DISCONNECT = b'\x05'
