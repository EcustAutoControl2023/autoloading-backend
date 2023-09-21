import datetime
import socket,time
import threading
from flask import Flask, current_app, jsonify
from autoloading.models import db
from autoloading.models.sensor import Sensor

server_ip=('192.168.100.8',8234)
hex_data='0103200200012E0A'
byte_data = bytes.fromhex(hex_data)
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
running = False
int_distance = 0
timer = None


def read_per_second():
    global int_distance
    global current_time
    global running
    while running:
        s.connect(server_ip)
        s.sendall(byte_data)
        received_data = s.recv(1024)
        hex_received_data = received_data.hex() # '010302157cb735'    
        current_time = datetime.datetime.now()
        hex_distance = hex_received_data[6:10]
        int_distance = int(hex_distance,16)
        #print('distance:', int_distance,'mm')
        s.close()
        insert_data(int_distance,current_time)
        #return int_distance

def test_save_data():
    current_time = datetime.datetime.now()
    int_distance = int('157C',16)
    insert_data(int_distance,current_time)
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