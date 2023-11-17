import datetime
import logging
import socket,time

from flask import jsonify
from autoloading.models import db
from autoloading.models.sensor import Sensor

server_ip=('192.168.100.8',8234)#相机的ip地址、端口号
hex_data='010320010001DE0A'#发送给物位计的命令
byte_data = bytes.fromhex(hex_data)
#s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)# TCP
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
s.setblocking(False)
running = True
int_distance = 0
timer = None


def read_per_second():#每秒读取一次物位计数据

    global int_distance
    global current_time
    global s
    global running
    from .socket import sensor_data

    received_data = -1

    while running:  
        # 发送modbus指令，接受数据
        s.sendto(byte_data, server_ip)
        while True:
            try:
                received_data,addr = s.recvfrom(1024)
            except socket.error as e:
                continue
            break
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
    if int_distance < 3000: # 确保存入有效数据
        sensor = Sensor(data=int_distance,time=current_time)
        db.session.add(sensor)
        db.session.commit()



# 开启请求物位计数据
def start():
    read_per_second()
    return '测量开始'

# 停止请求物位计数据
def stop():
    global running
    global s
    running = False
    s.close()
    return '测量停止'

