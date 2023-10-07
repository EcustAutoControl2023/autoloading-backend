from flask import request,jsonify, session
import datetime
from ..config import TRUCK_CONFIRM

# 返回默认值
default_os:dict={
    "truck_id": "闽D123456",     # 车牌号
    "work_total": 1,             # 作业总次数
    "work_weight_list": 0,       # 每次作业装料重量
    "work_weight_status": 0,     # 作业执行情况 0 未开始 1 正在执行 2 已完成 3 检测溢出被动完成
    "work_weight_reality": 0,    # 作业装料重量情况
    "flag_load": 0,              # 装料机状态 0 未装车 1 装车中 2 故障
    "height_load": 0,            # 料高（目前装料点）
    "allow_work_flag": 0,        # 允许作业标志 1允许 0不允许
    "allow_plc_work": 0          # PLC启停控制 1启动 0停止
}

# 生成返回值
def gen_return_data(
        store_id: int=1,
        loader_id: int=20,
        operating_stations: dict={},
    ):
    global default_os
    # 服务器返回时间
    res_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    # osi中缺失的值使用默认值填充
    res_os = default_os.copy()
    res_os.update(operating_stations)
    # 返回json格式
    return {
        "time": res_time,
        "store_id": store_id,
        "loader_id": loader_id,
        "operating_stations": res_os,
    }

#@app.route('/connect',methods=['POST'])
def connect():
    global TRUCK_CONFIRM
    data = request.get_json()
    data_type = data.get('data_type')
    # 客户端请求时间
    # time = datetime.datetime.now()
    req_time = data.get('time')
    operating_stations = data.get('operating_stations')
    truck_id = operating_stations.get('truck_id') 
    box_length = operating_stations.get('box_length') 
    box_width = operating_stations.get('box_width') 
    box_height = operating_stations.get('box_height') 
    distance_0 = operating_stations.get('distance_0') 
    distance_1 = operating_stations.get('distance_1') 
    distance_2 = operating_stations.get('distance_2')
    truck_load = operating_stations.get('truck_load') 
    load_current = operating_stations.get('load_current')
    truck_weight_in = operating_stations.get('truck_weight_in') 
    truck_weight_out = operating_stations.get('truck_weight_out') 
    goads_type = operating_stations.get('goads_type') 
    store_id = operating_stations.get('store_id') 
    loader_id = operating_stations.get('loader_id') 
    flag_operate = operating_stations.get('flag_operate') 
    allow_work_flag = operating_stations.get('allow_work_flag') 
    allow_plc_work = operating_stations.get('allow_plc_work') 
    picture_url_plate = operating_stations.get('picture_url_plate', 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')
    picture_url_request = operating_stations.get('picture_url_request','https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')


    if data_type == 0:
        # TODO: 接收到客户端请求，计算并发送装车策略

        work_total = 1
        work_weight_list = [10]

        result = gen_return_data(
            store_id=store_id, 
            loader_id=loader_id,
            operating_stations={
                "allow_work_flag": allow_work_flag,
                "work_total": work_total,
                "work_weight_list": work_weight_list,
            })

    elif data_type == 1:
        # TODO: 请求作业允许

        # 中控确认标志
        truck_id_confirm = session.get('center_popup_confirm', False)

        if not truck_id_confirm:
            # 弹出物料确认窗口
            from .socket import center_popup
            center_popup({'img_url': picture_url_request})

            session['center_popup_confirm'] = TRUCK_CONFIRM.get()
            truck_id_confirm = session['center_popup_confirm']

        # 中控确认，允许作业
        allow_work_flag = 1 if truck_id_confirm else 0
        allow_plc_work = 1 if truck_id_confirm else 0

        if allow_work_flag == 1:
            # 发送信号，控制系统开始送料、下料
            # TODO: 物位计数据读取和计算 以及判断任务是否完成
            work_weight_status = 0  # 0 未开始 1 正在执行 2 已完成 3 检测溢出被动完成
            flag_load = 0  # 装料机状态 0 未装车 1 装车中 2 故障

            if work_weight_status == 2 and work_weight_status == 3:
                # 作业完成，发送信号，取消先前的中控确认，控制系统停止送料、下料
                flag_load = 0
                allow_plc_work = 0
                session['center_popup_confirm'] = False

            result = gen_return_data(
                store_id=store_id, 
                loader_id=loader_id,
                operating_stations={
                    "work_total": 1,
                    "work_weight_list": [10],
                    "allow_work_flag": allow_work_flag,
                    "allow_plc_work": allow_plc_work,
                    "work_weight_status": work_weight_status,
                    "flag_load": flag_load,
                })

        else :
            # TODO: 中控拒绝，不允许作业

            result = gen_return_data(
                store_id=store_id, 
                loader_id=loader_id,
                operating_stations={
                    "allow_work_flag": allow_work_flag,
                    "allow_plc_work": allow_plc_work,
                })

    elif data_type == 2:
        # TODO: 计算出闸量

        work_weight_reality = 8.9
        result = gen_return_data(
            store_id=store_id,
            loader_id=loader_id,
            operating_stations={
                "work_weight_reality": work_weight_reality,
            })

    elif data_type == 3:
        # TODO: 返回实时数据

        allow_work_flag = 1 if session['center_popup_confirm'] else 0
        allow_plc_work = 1 if session['center_popup_confirm'] else 0

        result = gen_return_data(
            store_id=store_id, 
            loader_id=loader_id,
            operating_stations={
                "truck_id": truck_id,
                # "work_total": work_total,
                # "work_weight_list": work_weight_list,
                # "work_weight_status": work_weight_status,
                # "work_weight_reality": work_weight_reality,
                # "flag_load": flag_load,
                # "height_load": height_load,
                "allow_work_flag": allow_work_flag,
                "allow_plc_work": allow_plc_work,
            })

    elif data_type == 4:
        # TODO: 车牌弹窗确认

        truck_id_confirm = session.get('truck_id_popup_confirm', False)
        if not truck_id_confirm:
            # 弹出车牌勘误窗口
            from .socket import truck_id_popup
            truck_id_popup({'img_url': picture_url_request})

            session['truck_id_popup_confirm'] = TRUCK_CONFIRM.get()
            truck_id_confirm = session['truck_id_popup_confirm']

        result = gen_return_data(
            store_id=store_id, 
            loader_id=loader_id,
            operating_stations={
                truck_id: truck_id,
            })


    else:
        result = {'message': '无请求参数 KEY/VALUE 类型'}
    
    return jsonify(result)


# 清除session，测试用
def clear_session(opt=['truck_id_popup_confirm', 'center_popup_confirm']):
    for key in opt:
        del session[key]
    return 'clear session success'