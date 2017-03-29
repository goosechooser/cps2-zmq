# pylint: disable=E1101
import time
from threading import Thread
import zmq
import msgpack

# a mock mame server for debugging client side
# a mock client for debugging server side
class Publisher(Thread):
    def __init__(self, port, context=None):
        super(Publisher, self).__init__()
        self._context = context or zmq.Context.instance()
        self._publisher = self._context.socket(zmq.PUB)
        self._publisher.bind(':'.join(["tcp://*", str(port)]))

    def run(self):
        i = 0
        time.sleep(10)
        while i < 10:
            print('sending')
            self._publisher.send_json({'frame' : i})
            i += 1
            time.sleep(2)

        self._publisher.send_json({'frame' : 'closing'})
        print('done')

class MockServer():
    def __init__(self, port, context=None):
        self._context = context or zmq.Context.instance()
        self._subscriber = self._context.socket(zmq.SUB)
        self._subscriber.connect(':'.join(["tcp://localhost", str(port)]))
        self._subscriber.setsockopt_string(zmq.SUBSCRIBE, '')

        # self._publisher = Publisher(port + 1)

    def run(self):
        print("starting server")

        message = 'ok'
        # while message != "closing":
        for i in range(2000):
            message = self._subscriber.recv()
            # print('message', message)
            # print('message type', type(message))

            message = msgpack.unpackb(message, encoding='utf-8')
            print('frame number', message['frame_number'])
            # print('palettes', message['palettes'])
            print('sprites', message['sprites'])
            print('type o sprites', type(message['sprites']))

            message = message['frame_number']
            # print(message)
        print('donezo')


def main():
    server = MockServer(5556)
    time.sleep(1)
    server.run()

if __name__ == '__main__':
    main()

