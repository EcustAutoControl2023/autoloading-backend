import logging
from flask import jsonify, request
from autoloading.models import db
from autoloading.models.sensor import Traffic
import datetime


# TODO: 实现功能：车辆信息更新
def update_truck_content(truckid:str, loaderid, update_data:dict):
    traffic = Traffic.query.filter_by(truckid=truckid, loaderid=loaderid).order_by(Traffic.id.desc()).first()
    # FIXME: 打印车辆数据
    # logging.debug(traffic)
    for key, value in update_data.items():
        if 'truck_weight_out' == key:
            traffic.truckweightout = value
        elif 'load_start_time' == key:
            traffic.loadstarttime = value
        elif 'load_level_height1' == key:
            traffic.loadlevelheight1 = value
        elif 'load_level_height2' == key:
            traffic.loadlevelheight2 = value
        elif 'load_level_height3' == key:
            traffic.loadlevelheight3 = value
        elif 'load_time1' == key:
            traffic.loadtime1 = value
        elif 'load_time2' == key:
            traffic.loadtime2 = value
        elif 'load_time3' == key:
            traffic.loadtime3 = value
        elif 'loadestimate' == key:
            traffic.loadestimate = value
        elif 'loadstatus' == key:
            traffic.loadstatus = value

    db.session.commit()
    from .socket import traffic_data, overview_data_request
    traffic_data({
        'truckid': traffic.truckid,
        'truckweightin': traffic.truckweightin,
        'truckweightout': traffic.truckweightout,
        'goodstype': traffic.goodstype,
        'truckload': traffic.truckload,
        'loadcurrent': traffic.loadcurrent,
        'storeid': traffic.storeid,
        'loaderid': traffic.loaderid,
        'modified': True
    })
    overview_data_request(1) # 更新总览

#@app.route('/store', methods=['POST'])  
def insert_truck_content(req_time,
                         truck_id,
                         truck_load,
                         load_current,
                         box_length,
                         box_width,
                         box_height,
                         truck_weight_in,
                         truck_weight_out, # 需要更新
                         goods_type,
                         store_id,
                         loader_id,
                         load_level_height1, # 需要更新
                         load_level_height2, # 需要更新
                         load_level_height3, # 需要更新
                         load_start_time, # 需要更新
                         load_time1, # 需要更新
                         load_time2, # 需要更新
                         load_time3, # 需要更新
                         work_total,
                         load_estimate, # 需要更新
                         jobid,
                         loadstatus, # 需要更新
                         location,
                         stackpos
                         ):
    # load_level_height1: 物位计第一次装车高度
    # load_level_height2: 物位计第二次装车高度
    # load_level_height3: 物位计第三次装车高度
    # load_time1: 第一次装车结束时间
    # load_time2：第二次装车结束时间
    # load_time3：第三次装车结束时间
    traffic = Traffic(time = req_time,
                      truckid=truck_id,
                      truckload = truck_load,
                      boxlength = box_length,
                      boxwidth = box_width,
                      boxheight = box_height,
                      truckweightin = truck_weight_in,
                      truckweightout = truck_weight_out,
                      goodstype = goods_type,
                      storeid = store_id,
                      loaderid = loader_id,
                      loadlevelheight1 = load_level_height1,
                      loadlevelheight2 = load_level_height2,
                      loadlevelheight3 = load_level_height3,
                      loadstarttime = load_start_time,
                      loadtime1 = load_time1,
                      loadtime2 = load_time2,
                      loadtime3 = load_time3,
                      loadcurrent = load_current,
                      worktotal = work_total,
                      loadestimate = load_estimate,
                      jobid=jobid,
                      loadstatus=loadstatus,
                      location=location,
                      stackpos=stackpos
)
    db.session.add(traffic)
    db.session.commit()
    from .socket import traffic_data, overview_data_request
    traffic_data({
        'truckid': truck_id,
        'truckweightin': truck_weight_in,
        'truckweightout': truck_weight_out,
        'goodstype': goods_type,
        'truckload': truck_load,
        'loadcurrent': load_current,
        'storeid': store_id,
        'loaderid': loader_id,
        'modified': False
    })
    overview_data_request(1) # 更新总览

#更新车辆数据函数测试
#@app.route('/update', methods=['POST'])  
def update():
    data = request.get_json()

    update_truck_content(data.get('truckid'), data.get('loaderid'), data.get('update_data'))

    return jsonify("{'code': 'ok'}")

