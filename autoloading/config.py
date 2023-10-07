from queue import Queue

ENV = 'development'
# ENV = 'production'
SECRET_KEY = 'development key'

TRUCK_CONFIRM = Queue()

# 传感器数据请求任务标志位
MEASURE_START = False