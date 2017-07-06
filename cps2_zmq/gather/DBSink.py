# pylint: disable=E1101
"""
DBSink.py
"""

import sys
import json
from threading import Thread
import msgpack
import zmq
import pymongo

class DBSink(Thread):
    """
    """
    def __init__(self, idn, front_addr, db, context=None):
        super(DBSink, self).__init__()
        self.idn = bytes(idn, encoding='UTF-8')
        self.context = context or zmq.Context.instance()

        self.front = self.context.socket(zmq.ROUTER)
        self.front.setsockopt(zmq.IDENTITY, self.idn)
        self.front.bind(front_addr)

        self.client = pymongo.MongoClient()
        self.db = self.client[db]

        self.msgs_recv = 0

    def close(self):
        """
        Closes all sockets.
        """
        self.front.close()
        self.client.close()

    def run(self):
        working = True
        sources = {}
        while working:
            worker_addr, _, message = self.front.recv_multipart()
            sources[worker_addr] = 'ok'
            
            if message == b'END':
                print("SINK got", message)
                sys.stdout.flush()
                del sources[worker_addr]
                if not sources:
                    working = False
                # self.front.send_multipart([b'empty', message])
            else:
                self.msgs_recv += 1
                unpacked = msgpack.unpackb(message, encoding='utf-8')
                self.process(unpacked)

        self.close()
        self.report()

    def report(self):
        """
        Report stats at the end.
        """
        print(self.__class__.__name__, self.idn, 'received', self.msgs_recv, 'messages')
        sys.stdout.flush() 

    def process(self, message):
        try:
            json_ = json.loads(message)
            self.db.frames.insert_one(json_)
        except Exception as err:
            print(err)
            sys.stdout.flush()