import logging
from flask import session
from flask_socketio import SocketIO,emit
from ..config import TRUCK_CONFIRM, MEASURE_START
from .sensor import start
from autoloading.models.sensor import Traffic
from flask import Flask, jsonify



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


# 向前端发送最近n条车辆数据
def traffic_data_history(data):
    global socketio
    ret = list()
    for traffic_data in data:
        ret.append({
            'truckid': traffic_data.truckid,
            'truckweightin': traffic_data.truckweightin,
            'truckweightout': traffic_data.truckweightout,
            'goodstype': traffic_data.goodstype,
            'truckload': traffic_data.truckload,
            'loadcurrent': traffic_data.loadcurrent,
            'storeid': traffic_data.storeid,
            'loaderid': traffic_data.loaderid,
        })
        # logging.debug(ret)
    socketio.emit('traffic_data_queue', ret)

# 接受前端发送的车辆数据请求，会有数量参数data['data']
@socketio.on('traffic_data_request')
def traffic_data_request(data):
    traffics = Traffic.query.order_by(Traffic.id.desc()).limit(data['data']).all()
    logging.debug(traffics)
    traffic_data_history(list(reversed(traffics)))

# 向前端发送数据库最新数据
def traffic_data(data):
    global socketio
    socketio.emit('traffic_data', data)
