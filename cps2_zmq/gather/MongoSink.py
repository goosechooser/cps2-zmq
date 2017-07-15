# pylint: disable=E1101
"""
BaseSink.py
"""

import sys
import json
import zmq
import pymongo
from pymongo.errors import ConnectionFailure
from cps2_zmq.gather.BaseSink import BaseSink

class MongoSink(BaseSink):
    """
    Uploads to a mongodb.
    """
    def __init__(self, idn, front_addr, service, sub_addr, topics, db):
        self.client = None
        self.db = db
        super(MongoSink, self).__init__(idn, front_addr, service, sub_addr, topics)

    def conn_db(self):
        self.client = pymongo.MongoClient()
        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
        except ConnectionFailure:
            print(self.__class__.__name__, self.idn, "mongo server not available")
            sys.stdout.flush()
            self.disconnect(self.frontstream)
        else:
            print(self.__class__.__name__, self.idn, "connected to mongo database")
            sys.stdout.flush()
            self.db = self.client[self.db]

    def setup(self):
        super(MongoSink, self).setup()
        self.conn_db()

    def close(self):
        if self.client:
            self.client.close()
        super(MongoSink, self).close()

    def process_pub(self, message):
        coll = 'test_frames'
        try:
            json_ = json.loads(message)
            self.db[coll].insert_one(json_)
        except Exception as err:
            print(err)
            sys.stdout.flush()

if __name__ == '__main__':
    sink = MongoSink("sink-1", "tcp://127.0.0.1:5557", b'logging', "tcp://127.0.0.1:5558", "frame", "cps2")
    sink.start()
    sink.close()
    sink.report()
