import datetime
import logging
import socket,time

from flask import jsonify
from autoloading.models import db
from autoloading.models.sensor import Sensor

server_ip=('192.168.100.8',8234)#相机的ip地址、端口号
hex_data='010320010001DE0A'#发送给物位计的命令
byte_data = bytes.fromhex(hex_data)
# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)# TCP
# s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
running = True
timer = None

# 测试
import pandas as pd
# 从csv文件中读取数据
sdata = pd.read_csv('sensor1020.csv')
sdata_step = 0
sdata_len = len(sdata) - 1


def simulation_data():
    global sdata
    global sdata_len
    global sdata_step
    time_str = sdata.iloc[sdata_step]['time']
    time_obj = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
    int_distance = sdata.iloc[sdata_step]['data']
    sdata_step += 1
    return int_distance,time_obj

def read_per_second_simulation():#每秒读取一次物位计数据
        global running
        from .socket import sensor_data
    
        while running:  
            int_distance,current_time = simulation_data()
            # logging.debug('current_time: %s',current_time)
            # logging.debug('int_distance: %s',int_distance)
            latest_data = Sensor.query.order_by(Sensor.id.desc()).first()
            if (latest_data is None) or ((current_time - latest_data.time).total_seconds() > 1):
                insert_data(int_distance,current_time)
            
            # 发送物位计数据到前端
            sensor_data({
                'value': int(int_distance)
            })
            time.sleep(1)


def read_per_second():#每秒读取一次物位计数据

    global current_time
    global s
    global running
    from .socket import sensor_data


    while running:  
        # 发送modbus指令，接受数据
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
        s.connect(server_ip)
        s.sendto(byte_data)
        received_data = s.recvfrom()
        hex_received_data = received_data.hex()  
        current_time = datetime.datetime.now()
        hex_distance = hex_received_data[6:10]
        int_distance = int(hex_distance,16)
        latest_data = Sensor.query.order_by(Sensor.id.desc()).first()
        if (latest_data is None) or ((current_time - latest_data.date).total_seconds > 1):
            insert_data(int_distance,current_time)
        
        # 发送物位计数据到前端
        sensor_data({
            'value': int_distance
        })
        time.sleep(1)
        s.close()

# 将测量值和时间存储在数据库中
def insert_data(int_distance,current_time):
    # logging.debug('insert data')
    # XXX:滤波，至少5个数据（线性变化，
    if int_distance < 3500: # 确保存入有效数据
        sensor = Sensor(data=int_distance,time=current_time)
        db.session.add(sensor)
        db.session.commit()



# 开启请求物位计数据
def start():
    read_per_second_simulation()
    return '测量开始'

def restart():
    global running
    global sdata_step
    sdata_step = 0
    running = False
    running = True
    read_per_second_simulation()
    return '测量重新开始'

# 停止请求物位计数据
def stop():
    global running
    running = False
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