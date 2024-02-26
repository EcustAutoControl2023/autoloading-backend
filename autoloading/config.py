from queue import Queue
import os
import errno
import logging


# apscheduler 任务启动状态
RUNNING = True

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

# 日志配置
LOGPATH = os.environ.get('LOGFOLDER','logs')
FILENAME = os.environ.get('LOGFILE', "stdout.log")
LOG_DICT = {}
LOG_FORMATTER = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)-5.5s] [%(filename)s:%(lineno)d] %(message)s")


# 检查文件夹是否存在
def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

# 创建logger
def create_logger(logfile):
    global sub_logger
    sub_logger = LOG_DICT.get(logfile, None)
    if sub_logger is None:
        sub_logger = logging.getLogger(logfile)
        sub_logger.name = logfile
        fileHandler1 = logging.FileHandler("{0}/{1}".format(LOGPATH, 'process_'+str(logfile)+'.log'))
        fileHandler1.setFormatter(LOG_FORMATTER)
        sub_logger.addHandler(fileHandler1)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(LOG_FORMATTER)
        sub_logger.addHandler(consoleHandler)
        sub_logger.setLevel("DEBUG")
        sub_logger.propagate = False
        LOG_DICT.__setitem__(logfile, sub_logger)

    return sub_logger

def setup_logging():
    mkdir_p("{0}".format(LOGPATH))
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)
    logging.getLogger('apscheduler.scheduler').setLevel(logging.ERROR)
    class NoRunningFilter(logging.Filter):
        def filter(self, record):
            return not record.msg.startswith('Running job')

    my_filter = NoRunningFilter()
    logging.getLogger("apscheduler.scheduler").addFilter(my_filter)
