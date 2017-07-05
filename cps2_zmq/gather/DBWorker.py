# pylint: disable=E1101

import pymongo
import json
from cps2_zmq.gather.BaseWorker import BaseWorker

# Refactor this to be DBWorker
# Refactor MameWorker into an abstract [] Worker class
class DBWorker(BaseWorker):
    """
    JSON-ifies messages and uploads them to a db
    """
    def __init__(self, idn, front_addr, db, context=None):
        super(DBWorker, self).__init__(idn, front_addr)

        self.client = pymongo.MongoClient()
        self.db = self.client[db]

    def close(self):
        super(DBWorker, self).close()
        self.client.close()

    def process(self, message):
        try:
            json_ = json.loads(message)
            self.db.frames.insert_one(json_)
        except Exception as err:
            print(err)

def database_active():
    """
    If a mongodb instance is running, return a connection.
    """
    maxSevSelDelay = 1
    try:
        client = pymongo.MongoClient("someInvalidURIOrNonExistantHost",
                                    serverSelectionTimeoutMS=maxSevSelDelay)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)
    else:
        return client
            

