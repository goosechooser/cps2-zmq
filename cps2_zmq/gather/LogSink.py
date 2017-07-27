# pylint: disable=E1101
"""
BaseSink.py
"""
from cps2_zmq.gather.BaseSink import BaseSink

# Filters/Handlers/Loggers would do bulk of work here
class LogSink(BaseSink):
    def handle_pub(self, msg):
        """
        Figure out extent to which this'll be overridden.
        """
        self.msgs_recv += 1
        self._logger.info('Received message %s', msg)

        topic = msg.pop(0).decode('utf-8')
        log = msg.pop().decode('utf-8')

        self._logger.info('topic %s', topic)
        self._logger.info('message %s', log)

        topic_split = self.handle_topic(topic)
        print('topic_split', topic_split)

        self.handle_log(log)

    def handle_topic(self, topic):
        return topic.split('.')

    def handle_log(self, log):
        print('handle_log', log)

if __name__ == '__main__':
    sink = LogSink("1", "tcp://127.0.0.1:5557", "tcp://127.0.0.1:5558", ['MameWorker'])
    sink.start()
    sink.report()
    sink.close()
