from flask import request,jsonify, session
import datetime
import logging
from ..config import TRUCK_CONFIRM
from .loaderpoint import LoadPoint, load_point_dict


#@app.route('/connect',methods=['POST'])
def connect():
    global load_point_dict

    data = request.get_json()
    data_type = data.get('data_type', None)
    # req_time = data.get('time', None)
    req_time = datetime.datetime.now()
    operating_stations = data.get('operating_stations', None)
    job_id = operating_stations.get('job_id', None)
    truck_id = operating_stations.get('truck_id', None)
    box_length = operating_stations.get('box_length', None)
    box_width = operating_stations.get('box_width', None)
    box_height = operating_stations.get('box_height', None)
    distance_0 = operating_stations.get('distance_0', None)
    distance_1 = operating_stations.get('distance_1', None)
    distance_2 = operating_stations.get('distance_2', None)
    truck_load = operating_stations.get('truck_load', None)
    load_current = operating_stations.get('load_current', None)
    truck_weight_in = operating_stations.get('truck_weight_in', None)
    truck_weight_out = operating_stations.get('truck_weight_out', None)
    truck_weight_out = 0 if (truck_weight_out is None) or (len(truck_weight_out) == 0) else truck_weight_out
    goods_type = operating_stations.get('goods_type', None)
    store_id = operating_stations.get('store_id', None)
    loader_id = operating_stations.get('loader_id', None)
    #flag_operate = operating_stations.get('flag_operate', None )
    #allow_work_flag = operating_stations.get('allow_work_flag', None )
    #allow_plc_work = operating_stations.get('allow_plc_work', None)
    picture_url_plate = operating_stations.get('picture_url_plate', 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')
    picture_url_request = operating_stations.get('picture_url_request','https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')
    breakdowncode = operating_stations.get('breakdowncode', None)


    return_data = load_point_dict.get(loader_id).load_control(
        req_time=req_time, data_type=data_type,
        truck_id=truck_id, truck_load=truck_load,
        box_length=box_length, box_width=box_width, box_height=box_height,
        truck_weight_in=truck_weight_in, truck_weight_out=truck_weight_out,
        goods_type=goods_type, store_id=store_id, loader_id=loader_id,
        load_current=load_current, 
        distance0=distance_0, distance1=distance_1, distance2=distance_2,
        picture_url_plate=picture_url_plate, picture_url_request=picture_url_request
    )

    return return_data


# 清除session，测试用
def clear_session(opt=['truck_id_popup_confirm', 'center_popup_confirm']):
    for key in opt:
        del session[key]
    return 'clear session success'
