# pylint: disable=E1101
"""
BaseSink.py
"""

import sys
import json
import zmq
import pymongo
from cps2_zmq.gather.BaseSink import BaseSink

class MongoSink(BaseSink):
    """
    Uploads to a mongodb.
    """
    def __init__(self, idn, front_addr, service, sub_addr, topics, db):
        self.client = pymongo.MongoClient()
        self.db = db
        super(MongoSink, self).__init__(idn, front_addr, service, sub_addr, topics)

    def setup(self):
        self.db = self.client[self.db]
        super(MongoSink, self).setup()

    def close(self):
        self.client.close()
        super(MongoSink, self).close()

    def process_pub(self, message):
        coll = 'test_frames'
        try:
            json_ = json.loads(message)
            self.db.coll.insert_one(json_)
        except Exception as err:
            print(err)
            sys.stdout.flush()
