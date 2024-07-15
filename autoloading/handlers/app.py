from flask import request
from .loaderpoint import load_point_dict



#@app.route('/connect',methods=['POST'])
def connect():
    global load_point_dict

    data = request.get_json()
    data_type = data.get('data_type', None)
    req_time = data.get('time', None)
    operating_stations = data.get('operating_stations', None)
    temp_manual_stop = operating_stations.get('temp_manual_stop',0)
    job_id = operating_stations.get('job_id', None)
    truck_id = operating_stations.get('truck_id', None)
    box_length = operating_stations.get('box_length', None)
    box_width = operating_stations.get('box_width', None)
    box_height = operating_stations.get('box_height', None)
    distance_0 = operating_stations.get('distance_0', None)
    distance_1 = operating_stations.get('distance_1', None)
    distance_2 = operating_stations.get('distance_2', None)
    truck_load = operating_stations.get('truck_load', None)
    load_current = operating_stations.get('load_current', 0)
    truck_weight_in = operating_stations.get('truck_weight_in', None)
    truck_weight_out = operating_stations.get('truck_weight_out', None)
    truck_weight_out = 0 if (truck_weight_out is None) or (isinstance(truck_weight_out, dict) or (isinstance(truck_weight_out, list))) else truck_weight_out
    goods_type = operating_stations.get('goods_type', None)
    store_id = operating_stations.get('store_id', None)
    loader_id = str.upper(operating_stations.get('loader_id', None))
    picture_url_plate = operating_stations.get('picture_url_plate', 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')
    picture_url_request = operating_stations.get('picture_url_request','https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')
    icps_differ_current = operating_stations.get('icps_differ_current', None)
    loading_state = operating_stations.get('loading_state', None)
    type_of_opening = operating_stations.get('type_of_opening',None)
    opening_length_bias = operating_stations.get('opening_length_bias',None)
    opening_width_bias = operating_stations.get('opening_width_bias',None)
    opening_length = operating_stations.get('opening_length',None)
    opening_width = operating_stations.get('opening_width',None)
    breakdowncode = operating_stations.get('breakdowncode', None)
    emergency_stop = operating_stations.get('emergency_stop', None)
    auto_select = operating_stations.get('auto_select', None)
    belt_motor_run = operating_stations.get('belt_motor_run', None)

    if data_type == 2:
        return_data = load_point_dict[loader_id].update_weightout(
            distance_0=distance_0, distance_1=distance_1, distance_2=distance_2,
            truck_id=truck_id, loader_id=loader_id, req_time=req_time,
            store_id=store_id, truck_weight_out=truck_weight_out
        )
    else:
        return_data = load_point_dict[loader_id].load_control(
            req_time=req_time, data_type=data_type,
            truck_id=truck_id, truck_load=truck_load,temp_manual_stop=temp_manual_stop,
            box_length=box_length, box_width=box_width, box_height=box_height,
            truck_weight_in=truck_weight_in, truck_weight_out=truck_weight_out,
            goods_type=goods_type, store_id=store_id, loader_id=loader_id,
            load_current=load_current,
            distance0=distance_0, distance1=distance_1, distance2=distance_2, icps_differ_current=icps_differ_current,
            picture_url_plate=picture_url_plate, picture_url_request=picture_url_request,
            jobid=job_id,loading_state=loading_state,type_of_opening=type_of_opening,
            opening_length_bias=opening_length_bias,opening_width_bias=opening_width_bias,
            opening_length=opening_length,opening_width=opening_width,
            breakdowncode=breakdowncode,emergency_stop=emergency_stop,auto_select=auto_select,
            belt_motor_run=belt_motor_run
        )

    return return_data

