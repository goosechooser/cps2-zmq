"""
Just inserts a folder of data to mongoDB database.
"""
import json
import os
import pymongo

def main(coll, folder):
    client = pymongo.MongoClient()
    db = client[coll]
    for file_ in os.listdir(folder):
        with open(os.path.join(folder, file_), 'r') as f:
            read = f.read()

        decode = json.loads(read)
        db.frames.insert_one(decode)

    client.close()
    print('done')

def qdb(coll):
    client = pymongo.MongoClient()
    db = client['cps2']
    frames = db['frames']
    print(frames.count())

    for frame in frames.find(limit=5):
        print(frame)

    client.close()
    print('done')


if __name__ == '__main__':
    # main('cps2', 'D:\\Code\\production_data\\')
    qdb('csp2')
