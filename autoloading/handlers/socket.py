import logging
import re
from flask import session
from flask_socketio import SocketIO
from ..config import TRUCK_CONFIRM, MEASURE_START
from autoloading.models.sensor import Traffic
from autoloading.config import LOADER


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
        # FIXME: 打印车辆数据列表
        # logging.debug(ret)
    socketio.emit('traffic_data_queue', ret)

# 接受前端发送的车辆数据请求
# @data: data['data']取值为前端请求数据数量
@socketio.on('traffic_data_request')
def traffic_data_request(data):
    global LOADER
    # FIXME: 打印前端发送的请求数据
    logging.debug(f'#####traffic_data_request->data: { data }')
    traffics = Traffic.query.filter_by(loaderid=LOADER.queue[0]).order_by(Traffic.id.desc()).limit(data['number']).all()
    # FIXME: 打印后端返回的车辆数据
    logging.debug(f'#####traffic_data_request->traffics: { traffics }')
    traffic_data_history(list(reversed(traffics)))

# 向前端发送数据库最新数据
def traffic_data(data):
    global socketio
    global LOADER
    if data['loaderid'] == LOADER.queue[0]:
        socketio.emit('traffic_data', data)

# 切换当前的，获取loaderid
@socketio.on('tab_switch')
def tab_switch(data):
    global LOADER

    # FIXME: 打印当前选择的页面的数据表名
    logging.debug(f'####tab_switch: { data }')

    # 清空队列
    while not LOADER.empty():
        LOADER.get()

    LOADER.put(data['loader'])

def control_status_socket(val):  #发送控制器状态
    global socketio
    socketio.emit('control_status', val)

def loader_status_socket(val):  #发送装车状态
    global socketio
    socketio.emit('loading_status', val)

@socketio.on('overview_data_request')
def overview_data_request(data):
    # FIXME: 打印前端发送的请求数据
    logging.debug(f'#####traffic_data_request->data: { data }')
    traffics = list()
    for loadid in range(1, 21):
        traffic = Traffic.query.filter_by(loaderid=loadid).order_by(Traffic.id.desc()).first()
        traffics.append(traffic)
    # FIXME: 打印后端返回的车辆数据
    logging.debug(f'#####traffic_data_request->traffics: { traffics }')
    overview_data_history(list(reversed(traffics)))

def overview_data_history(data):
    global socketio
    def getdata(data, field):
        if data is None:
            return None
        try:
            ret = eval(f'data.{field}')
        except Exception:
            return None
        if ret is None:
            return None
        return ret
    ret = list()
    for overview_data in data:
        ret.append({
            'stackpos': getdata(overview_data, 'stackpos'),
            'location': getdata(overview_data, 'location'),
            'loadstatus': getdata(overview_data, 'loadstatus'),
            'loadheight': getdata(overview_data, 'loadheight'),
            'jobid': getdata(overview_data, 'jobid'),
            'truckid': getdata(overview_data, 'truckid'),
            'boxwidth': getdata(overview_data, 'boxwidth'),
            'boxheight': getdata(overview_data, 'boxheight'),
            'loadpoint1': getdata(overview_data, 'loadpoint1'),
            'loadpoint2': getdata(overview_data, 'loadpoint2'),
            'loadpoint3': getdata(overview_data, 'loadpoint3'),
            'truckload': getdata(overview_data, 'truckload'),
            'loadcurrent': getdata(overview_data, 'loadcurrent'),
            'truckweightin': getdata(overview_data, 'truckweightin'),
            'goodstype': getdata(overview_data, 'goodstype'),
        })
    socketio.emit('overview_data_queue', ret)
