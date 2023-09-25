from flask import session
from flask_socketio import SocketIO
from ..config import TRUCK_CONFIRM, MEASURE_START
from .sensor import start

socketio = SocketIO()


@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# 车牌弹窗
def truck_id_popup(data):
    global socketio
    socketio.emit('truck_id_popup', data)

@socketio.on('truck_id_popup_confirm')
def truck_id_popup_confirm(confirm):
    global TRUCK_CONFIRM
    session['truck_id_popup_confirm'] = confirm['data']
    TRUCK_CONFIRM.put(confirm['data']) 

# 中控弹窗
def center_popup(data):
    global socketio
    socketio.emit('center_popup', data)

@socketio.on('center_popup_confirm')
def center_popup_confirm(confirm):
    global TRUCK_CONFIRM
    session['center_popup_confirm'] = confirm['data']
    TRUCK_CONFIRM.put(confirm['data']) 

# 向前端发送传感器数据
def sensor_data(data):
    global socketio
    socketio.emit('sensor_data', data)

# 接受前端发送的传感器测量请求
@socketio.on('sensor_data_request')
def sensor_data_request(data):
    global MEASURE_START
    if not MEASURE_START:
        start()
        MEASURE_START = True