# pylint: disable=E1101
"""
BaseSink.py
"""

import sys
import json
import msgpack
import zmq
import pymongo
from pymongo.errors import ConnectionFailure
from cps2zmq.gather import BaseSink

class MongoSink(BaseSink):
    """
    Uploads to a mongodb.
    """
    def __init__(self, idn, front_addr, sub_addr, topics, db):
        self.client = None
        self.coll = topics
        self.db = db
        super(MongoSink, self).__init__(idn, front_addr, sub_addr, topics)

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
        try:
            unpacked = msgpack.unpackb(message, encoding='utf-8')
        except msgpack.exceptions.UnpackValueError as err:
            print(self.__class__.__name__, self.idn, err)
            sys.stdout.flush()
        else:
            json_ = json.loads(unpacked)
            self.db[self.coll].insert_one(json_)

if __name__ == '__main__':
    sink = MongoSink("1", "tcp://127.0.0.1:5557", "tcp://127.0.0.1:5558", "frame", "cps2")
    sink.start()
    sink.close()
    sink.report()
