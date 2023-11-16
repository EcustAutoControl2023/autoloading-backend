import datetime
import logging
import socket,time

from autoloading.models import db
from autoloading.models.sensor import loader_num
for i in range(loader_num):
    exec(f'from autoloading.models.sensor import Sensor{i+1}')

server_ip=('192.168.100.8',8234)#相机的ip地址、端口号
hex_data='010320010001DE0A'#发送给物位计的命令
byte_data = bytes.fromhex(hex_data)
#s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)# TCP
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
s.setblocking(False)
running = True
int_distance = 0
timer = None

def sread_per_second(Sensor):#每秒读取一次物位计数据
    # global int_distance
    # global current_time
    # global running
    from .socket import sensor_data


    # while running:  
    current_time = datetime.datetime.now()
    # logging.debug(f'Sensor is {Sensor}')
    if Sensor is Sensor1: 
        int_distance = int(5100)
    elif Sensor is Sensor2:
        int_distance = int(5200)
    elif Sensor is Sensor3:
        int_distance = int(5300)
    latest_data = Sensor.query.order_by(Sensor.id.desc()).first()
    # logging.debug(f'int_distance is {int_distance}')
    # if latest_data is not None:
    #     print(f'latest_data is {latest_data}')
    #     print(f'current_time - lastest_time is {current_time - latest_data.time}')
    if (latest_data is None) or ((current_time - latest_data.time).total_seconds() > 1):
        insert_data(Sensor, int_distance,current_time)
    
    # 发送物位计数据到前端
    sensor_data({
        'value': int_distance
    })
        # time.sleep(1)

def read_per_second(Sensor):#每秒读取一次物位计数据

    # global running
    from .socket import sensor_data

    received_data = -1

    # while running:  
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
    hex_distance = hex_received_data[6:10]
    int_distance = int(hex_distance,16)
    latest_data = Sensor.query.order_by(Sensor.id.desc()).first()
    if (latest_data is None) or ((current_time - latest_data.time).total_seconds() > 1):
        insert_data(Sensor, int_distance, current_time)
    
    # 发送物位计数据到前端
    sensor_data({
        'value': int_distance
    })
        # time.sleep(1)
    # s.close()

# 将测量值和时间存储在数据库中
def insert_data(Sensor, int_distance, current_time):
    # logging.debug('insert data')
    # XXX:滤波，至少5个数据（线性变化，
    if int_distance < 6000: # 确保存入有效数据
        # logging.debug(f'Sensor is {Sensor}')
        sensor = Sensor(data=int_distance,time=current_time)
        # logging.debug(f'sensor is {sensor}')
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



