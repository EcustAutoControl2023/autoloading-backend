from queue import Queue
import sys
import logging

ENV = 'development'
# ENV = 'production'
SECRET_KEY = 'development key'

TRUCK_CONFIRM = Queue()

# 传感器数据请求任务标志位
MEASURE_START = False

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(asctime)s][PID:%(process)d][%(levelname)s][%(name)s] %(message)s")
    handler.setFormatter(formatter)

    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
    class NoRunningFilter(logging.Filter):
        def filter(self, record):
            return not record.msg.startswith('Running job')

    my_filter = NoRunningFilter()
    logging.getLogger("apscheduler.scheduler").addFilter(my_filter)