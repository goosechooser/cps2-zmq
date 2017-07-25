# pylint: disable=E1101
"""
BaseSink.py
"""

import logging
from cps2_zmq.gather.BaseSink import BaseSink

class LogSink(BaseSink):
    def handle_pub(self, msg):
        """
        Figure out extent to which this'll be overridden.
        """
        self.msgs_recv += 1
        print(msg)
        topic = msg.pop(0).decode('utf-8')
        log = msg.pop().decode('utf-8')

        topic_split = self.handle_topic(topic)
        print('topic_split', topic_split)
        # if topic_split[-1] == 'WARN':
            # pass

        self.handle_log(log)

    def handle_topic(self, topic):
        return topic.split('.')

    def handle_log(self, log):
        print('handle_log', log)

if __name__ == '__main__':
    sink = LogSink("logsink-1", "tcp://127.0.0.1:5557", "tcp://127.0.0.1:5558", [''])
    sink.start()
    sink.close()
