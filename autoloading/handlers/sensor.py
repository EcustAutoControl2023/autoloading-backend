import datetime
import socket,time
import threading
from flask import Flask, current_app, jsonify
from autoloading.models import db
from autoloading.models.sensor import Sensor

server_ip=('192.168.100.8',8234)#相机的ip地址、端口号
hex_data='0103200200012E0A'#发送给物位计的命令
byte_data = bytes.fromhex(hex_data)
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
running = False
int_distance = 0
timer = None


def read_per_second():#每秒读取一次物位计数据
    global int_distance
    global current_time
    global running
    s.connect(server_ip)
    while running:  
        s.sendall(byte_data)
        received_data = s.recv(1024)
        hex_received_data = received_data.hex() 
        current_time = datetime.datetime.now()
        hex_distance = hex_received_data[6:10]
        int_distance = int(hex_distance,16)
        #print('distance:', int_distance,'mm')
        insert_data(int_distance,current_time)
        #return int_distance
        time.sleep(1)
    s.close()

def test_save_data():
    for i in range(1,100):
        current_time = datetime.datetime.now()
        int_distance = int('157c',16)
        insert_data(int_distance,current_time)
        from .socket import sensor_data
        sensor_data({
            'value': int_distance
        })

    return "success"




def test_read_data():
    # 拿到最近的一条数据
    sensor = Sensor.query.order_by(Sensor.id.desc()).first()
    ret = {
        'data': {
            'id': sensor.id,
            'distance': sensor.data,
            'time': sensor.time
        }
    }

    return jsonify(ret)


def insert_data(int_distance,current_time):#将测量值和时间存储在数据库中
    sensor = Sensor(data=int_distance,time=current_time)
    db.session.add(sensor)
    db.session.commit()


# def my_threading():
#     timer = threading.Timer(1,test_save_data,insert_data)
#     timer.start()


#@app.route("/start")
def start():#按下开始测量按键，读取物位计数据
    global running
    if not running:
        running = True
        threading.Thread(target=test_save_data).start()
    return '测量开始'

#@app.route("/stop")
def stop():#按下停止测量按键，停止读取物位计数据
    global running
    running = False
    return '测量停止'
