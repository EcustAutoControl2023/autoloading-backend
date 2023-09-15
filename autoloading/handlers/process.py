from flask import redirect, request, jsonify, session, url_for

import datetime

# 返回默认值
default_osi:dict={
    "truck_id": "闽D123456",     # 车牌号
    "work_total": 1,             # 作业总次数
    "work_weight_list": 10,      # 每次作业装料重量
    "work_weight_status": 1,     # 作业执行情况 0 未开始 1 正在执行 2 已完成 3 检测溢出被动完成
    "work_weight_reality": 8.9,  # 作业装料重量情况
    "flag_load": 1,              # 装料机状态 0 未装车 1 装车中 2 故障
    "height_load": 2,            # 料高（目前装料点）
    "allow_work_flag": 1,        # 允许作业标志 1允许 0不允许
    "allow_plc_work": 1          # PLC启停控制 1启动 0停止
}

# 返回格式
def gen_return_data(
        store_id: int=1,
        loader_id: int=20,
        operating_stations: dict={},
        osi_in: dict={},
    ):
    global default_osi
    # osi中缺失的值使用默认值填充
    osi_out = {**default_osi, **osi_in}
    # 返回json格式
    return jsonify({
        # 返回2023/4/10 2:26:16 格式的日期
        "time": datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        "store_id": store_id,
        "loader_id": loader_id,
        "operating_stations": operating_stations,
        "operating_stations.truck_id": osi_out['truck_id'],
        "operating_stations.work_total": osi_out[ 'work_total' ],
        "operating_stations.work_weight_list": osi_out['work_weight_list'],
        "operating_stations.work_weight_status": osi_out['work_weight_status'],
        "operating_stations.work_weight_reality": osi_out['work_weight_reality'],
        "operating_stations.flag_load": osi_out['flag_load'],
        "operating_stations.height_load": osi_out['height_load'],
        "operating_stations.allow_work_flag": osi_out['allow_work_flag'],
        "operating_stations.allow_plc_work": osi_out['allow_plc_work']
    })

# 作业策略(data_type=0)
def task_policy(time: str, operating_stations: dict, osi_in: dict):
    osi_out:dict = {
        "work_total": 1, # 目前只考虑一次装载的情况
        "work_weight_list": [10],   
        "work_weight_status": 1,    
        "work_weight_reality": 8.9, 
        "flag_load": 1,             
        "height_load": 2,           
        "allow_work_flag": 1,       
        "allow_plc_work": 1         
    }

    return gen_return_data(store_id=osi_in['store_id'], loader_id=osi_in['loader_id'], operating_stations=operating_stations, osi_in=osi_out)

# 允许作业(data_type=1)
def allow_task(time: str, operating_stations: dict, osi_in: dict):
    osi_out:dict = { }
    return gen_return_data(store_id=osi_in['store_id'], loader_id=osi_in['loader_id'], operating_stations=operating_stations, osi_in=osi_out)

# 出闸重量(data_type=2)
def weight_out(time: str, operating_stations: dict, osi_in: dict):
    osi_out:dict = { }
    return gen_return_data(store_id=osi_in['store_id'], loader_id=osi_in['loader_id'], operating_stations=operating_stations, osi_in=osi_out)

# 实时作业情况数据(data_type=3)
def task_info(time: str, operating_stations: dict, osi_in: dict):
    osi_out:dict = { }
    return gen_return_data(store_id=osi_in['store_id'], loader_id=osi_in['loader_id'], operating_stations=operating_stations, osi_in=osi_out)

# 识别错误弹窗确认(data_type=4)
def error_confirm(time: str, operating_stations: dict, osi_in: dict):
    osi_out:dict = {}
    return gen_return_data(store_id=osi_in['store_id'], loader_id=osi_in['loader_id'], operating_stations=operating_stations, osi_in=osi_out)



def process():
    if request.method == 'POST':
        # 拿到request的json数据
        json_data = request.get_json()
        data_type = json_data['data_type']
        time = json_data['time']
        operating_stations = json_data['operating_stations']
        # operating_stations_info -> osi
        osi = {
            "truck_id": json_data['operating_stations.truck_id'],
            "box_length": json_data['operating_stations.box_length'],
            "box_width": json_data['operating_stations.box_width'],
            "box_height": json_data['operating_stations.box_height'],
            "distance_0": json_data['operating_stations.distance_0'],
            "distance_1": json_data['operating_stations.distance_1'],
            "distance_2": json_data['operating_stations.distance_2'],
            "truck_load": json_data['operating_stations.truck_load'],
            "load_current": json_data['operating_stations.load_current'],
            "truck_weight_in": json_data['operating_stations.truck_weight_in'],
            "truck_weight_out": json_data['operating_stations.truck_weight_out'],
            "goods_type": json_data['operating_stations.goods_type'],
            "store_id": json_data['operating_stations.store_id'],
            "loader_id": json_data['operating_stations.loader_id'],
            "flag_operate": json_data['operating_stations.flag_operate'],
            "picture_url_plate": json_data['operating_stations.picture_url_plate'],
            "picture_url_request": json_data['operating_stations.picture_url_request'],
        }

        if data_type == 0:
            # 处理作业策略
            ret = task_policy(time=time, operating_stations=operating_stations, osi_in=osi)
        elif data_type == 1:
            # 处理允许作业
            ret = allow_task(time=time, operating_stations=operating_stations, osi_in=osi)
        elif data_type == 2:
            # 处理出闸重量
            ret = weight_out(time=time, operating_stations=operating_stations, osi_in=osi)
        elif data_type == 3:
            # 处理实时作业情况数据
            ret = task_info(time=time, operating_stations=operating_stations, osi_in=osi)
        elif data_type == 4:
            # 处理识别错误弹窗确认
            ret = error_confirm(time=time, operating_stations=operating_stations, osi_in=osi)
        else:
            raise Exception('data_type error')

        return ret
    else:

        session['img_url'] = "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
        return redirect(url_for('popup'))
        return '不支持其他请求方式!'

