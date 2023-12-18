import datetime
import logging
import socket,time
import struct

from flask import jsonify
from autoloading.models import db
from autoloading.models.sensor import Sensor

server_ip=('192.168.100.8',8234)#相机的ip地址、端口号
hex_data = '01040A1100022216'
byte_data = bytes.fromhex(hex_data)
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

#    while running:  
        # 发送modbus指令，接受数据
    while True:
        try:
            s.sendto(byte_data, server_ip)
        except socket.error as e:
            continue
        break

    send_time = datetime.datetime.now()

    while True:
        try:
            received_data,addr = s.recvfrom(1024)
        except socket.error as e:
            delta_time = datetime.datetime.now() - send_time
            if delta_time.total_seconds() > 5:
                s.sendto(byte_data, server_ip)
                send_time = datetime.datetime.now()
            continue
        break

    hex_received_data = received_data.hex()  
    current_time = datetime.datetime.now()
    hex_distance = hex_received_data[6:14]
    int_ma = int(hex_distance, 16)
    # 交换高16位和低16位的数据
    swapped_ma = (int_ma & 0xFFFF0000) >> 16 | (int_ma & 0x0000FFFF) << 16
    # 将结果转换回十六进制字符串
    hex_num = format(swapped_ma, '08X')
    # 将16进制数转换为二进制数
    binary_num = bin(int(hex_num, 16))[2:].zfill(32)
    # 提取符号位、指数位和尾数位
    sign_bit = int(binary_num[0])
    exponent_bits = binary_num[1:9]
    mantissa_bits = binary_num[9:]
    # 计算指数值
    exponent = int(exponent_bits, 2) - 127
    # 计算尾数值
    mantissa = 1 + sum([int(mantissa_bits[i]) * (2 ** -(i + 1)) for i in range(23)])
    # 计算十进制浮点数的值
    decimal_num = (-1) ** sign_bit * mantissa * (2 ** exponent)
    result = round(decimal_num*1000,3)
    int_distance = int(result)
    latest_data = Sensor.query.order_by(Sensor.id.desc()).first()
    if (latest_data is None) or ((current_time - latest_data.time).total_seconds() > 1):
        insert_data(int_distance,current_time)
    
    # 发送物位计数据到前端
    sensor_data({
        'value': int_distance
    })
#    time.sleep(1)
#    s.close()

# 将测量值和时间存储在数据库中
def insert_data(int_distance,current_time):
    # logging.debug('insert data')
    # XXX:滤波，至少5个数据（线性变化，
    if int_distance > 1000: # 确保存入有效数据
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


