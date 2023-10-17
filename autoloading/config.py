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
    logging.getLogger().setLevel("DEBUG")
