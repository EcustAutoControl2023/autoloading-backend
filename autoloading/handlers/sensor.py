import datetime
import logging
import socket,time
import numpy as np

from flask import jsonify
from autoloading.models import db
from autoloading.models.sensor import Sensor

server_ip=('192.168.100.8',8234)#相机的ip地址、端口号
hex_data='0103200200012E0A'#发送给物位计的命令
hex_data1 = '0103200700013E0B'
byte_data = bytes.fromhex(hex_data)
byte_data1 = bytes.fromhex(hex_data1)
# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)# TCP
# s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
running = False
int_distance = 0
timer = None


def read_per_second():#每秒读取一次物位计数据

    global int_distance
    global current_time
    global s
    # global running
    from .socket import sensor_data

    # try 语句，防止连接失败
    #try:
        #s.connect(server_ip)
    #except Exception as e:
        #print(e)
        #s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #s.connect(server_ip)

    # while running:  
        # 发送modbus指令，接受数据
        #s.sendall(byte_data)
        # received_data = s.recv(1024)
    hex_received_data = '010302157cb735'#received_data.hex() 
    current_time = datetime.datetime.now()
    hex_distance = hex_received_data[6:10]
    int_distance = int(hex_distance,16)
    insert_data(int_distance,current_time)
    
    # 发送物位计数据到前端
    sensor_data({
        'value': int_distance
    })
    # s.close()

# 将测量值和时间存储在数据库中
def insert_data(int_distance,current_time):
    # logging.info('insert data')
    # XXX:滤波，至少5个数据（线性变化，
    if int_distance < 4200: # 确保存入有效数据
        sensor = Sensor(data=int_distance,time=current_time)
        db.session.add(sensor)
        db.session.commit()



# 开启请求物位计数据
def start():
    global running
    if not running:
        running = True
        read_per_second()
    return '测量开始'

# 停止请求物位计数据
def stop():
    global running
    global s
    running = False
    s.close()
    return '测量停止'


# #存数据测试
# def test_save_data():
#     for i in range(1,100):
#         current_time = datetime.datetime.now()
#         int_distance = int('157c',16)
#         insert_data(int_distance,current_time)
#         from .socket import sensor_data
#         sensor_data({
#             'value': int_distance
#         })

#     return "success"

# # 读数据测试
# def test_read_data():
#     # 拿到最近的一条数据
#     sensor = Sensor.query.order_by(Sensor.id.desc()).first()
#     ret = {
#         'data': {
#             'id': sensor.id,
#             'distance': sensor.data,
#             'time': sensor.time
#         }
#     }
#     #return jsonify(ret)


def check_level(car_edge_z, level_z, level_z_queue):
    # 200: 裕度
    level_z_limit = car_edge_z - 200
    level_z_new = level_z_filter(level_z_queue, level_z, level_z_limit)

def level_z_filter(level_z_queue, level_z, level_z_limit):
    # 滤波器
    level_z_queue.push(level_z)
    level_z_array = np.array(level_z_queue)
    # 车高小于2.8米
    level_z_array_new = level_z_array[level_z_array[:] > 2800]
    if len(level_z_array_new) > 5:
        level_z_mean = np.mean(level_z_array_new)
        if level_z_mean - 500 < level_z_array[-1] < level_z_mean + 500:
            level_z_real = level_z_array[-1]
        else:
            level_z_real = level_z_mean
    else:
        stone_z_real = 0
    if stone_z_real < level_z_limit:
        stone_z_real = 0
    return level_z_real