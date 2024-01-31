from queue import Queue
import sys
import logging

ENV = 'development'
# ENV = 'production'
SECRET_KEY = 'development key'

# 队列: 存储弹窗确认值
TRUCK_CONFIRM = Queue()

# 物位计状态队列
SENSOR_STATUS = Queue()

# 摄像头连接超时时间(s)
CAP_TIME_OUT = 60

# 传感器数据请求任务标志位
MEASURE_START = False

# 队列: 存储网页切换页面的标签
SHOW_TAB = Queue()

# 队列: 存储装料点id
LOADER = Queue()
LOADER.put(1)

def setup_logging():
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)
    logging.getLogger('apscheduler.scheduler').setLevel(logging.ERROR)
    class NoRunningFilter(logging.Filter):
        def filter(self, record):
            return not record.msg.startswith('Running job')

    my_filter = NoRunningFilter()
    logging.getLogger("apscheduler.scheduler").addFilter(my_filter)
