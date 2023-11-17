from flask import request,jsonify, session
import datetime
import logging
from ..config import TRUCK_CONFIRM
from autoloading.handlers.truck_store import insert_truck_content, update_truck_content
from autoloading.models.sensor import Traffic, Sensor

# 返回默认值
default_os:dict={
    "truck_id": "闽D123456",     # 车牌号
    "work_total": 2,             # 作业总次数
    "work_weight_list": 0,       # 每次作业装料重量
    "work_weight_status": [1,0],     # 作业执行情况 0 未开始 1 正在执行 2 已完成 3 检测溢出被动完成
    "work_weight_reality": [8.9,0],    # 作业装料重量情况
    "flag_load": 1,              # 装料机状态 0 未装车 1 装车中 2 故障
    "height_load": 2,            # 料高（目前装料点）
    "allow_work_flag": 1,        # 允许作业标志 1允许 0不允许
    "allow_plc_work": 1,          # PLC启停控制 1启动 0停止
    "time":"2023/4/10 2:26:16",
}

user = dict()
icps_differ = None
time_record_flag = True


# 生成返回值
def gen_return_data(
        time,
        store_id: int=1,
        loader_id: int=20,
        operating_stations: dict={},
    ):
    # global default_os
    # 服务器返回时间
    # res_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    # osi中缺失的值使用默认值填充
    # res_os = default_os.copy()
    res_os = dict()
    res_os.update(operating_stations)
    # 返回json格式
    return {
        "time": time,
        "store_id": store_id,
        "loader_id": loader_id,
        "operating_stations": res_os,
    }

#@app.route('/connect',methods=['POST'])
def connect():
    global TRUCK_CONFIRM
    global user
    global icps_differ

    data = request.get_json()
    data_type = data.get('data_type', None)
    # req_time = data.get('time', None)
    req_time = datetime.datetime.now()
    operating_stations = data.get('operating_stations', None)
    job_id = operating_stations.get('job_id', None)
    user['truck_id'] = operating_stations.get('truck_id', None)
    box_length = operating_stations.get('box_length', None)
    box_width = operating_stations.get('box_width', None)
    box_height = operating_stations.get('box_height', None)
    distance_0 = float(operating_stations.get('distance_0', None))
    distance_1 = float(operating_stations.get('distance_1', None))
    distance_2 = float(operating_stations.get('distance_2', None))
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

    user['work_weight_reality'] = None
    user['height_load'] = None
    user['allow_work_flag'] = None
    

    if data_type == 0:


        # TODO: 接收到客户端请求，计算并发送装车策略
        if (distance_0 != distance_1) and (distance_0 != distance_2) and (distance_1 != distance_2):
            user['work_total'] = 3
            icps_differ = '0123' # 共装车三次，三个装车点各不相同
            user['icps_differ'] = distance_0
        elif distance_0 == distance_1 and distance_1 != distance_2 :
            user['work_total'] = 2
            icps_differ = '0012' # 共装车两次，前装车点和中装车点相同
            user['icps_differ'] = distance_0
        elif distance_1 == distance_2 and distance_1 != distance_0 :
            user['work_total'] = 2
            icps_differ = '0112' # 共装车两次，中装车点和后装车点相同
            user['icps_differ'] = distance_0
        elif distance_0 == distance_1 == distance_2 :
            user['work_total'] = 1
            icps_differ = '0001' # 共装车一次，三个装车点相同
            user['icps_differ'] = distance_0
        else:
            user['work_total'] = 0
            icps_differ = None # 无装车策略
            user['work_finish'] = 1
        
        logging.debug(f'icps_differ: {icps_differ}')

        insert_truck_content(
            req_time=req_time,
            truck_id=user['truck_id'],
            truck_load=truck_load,
            box_length=box_length,
            box_width=box_width,
            box_height=box_height,
            truck_weight_in=truck_weight_in,
            truck_weight_out=truck_weight_out,
            goods_type=goods_type,
            store_id=store_id,
            loader_id=loader_id,
            load_current=load_current,
            work_total=user['work_total'],
            load_level_height1=0,
            load_level_height2=0,
            load_time1=datetime.datetime.now(),
            load_time2=datetime.datetime.now()
        )

        # 如果引导策略反馈的 icps_differ 为空，且 work_finish=1，标识任务完成
        user['work_finish'] = 0 if (icps_differ is None) and (user.get('work_finish', 1) ==1) else user.get('work_finish', 0)

        # user['icps_differ'] = icps_differ
        result = gen_return_data(
            time = req_time,
            store_id = store_id, 
            loader_id = loader_id,
            operating_stations={

                "truck_id" : user['truck_id'],
                "icps_differ" : icps_differ,

            })

    elif data_type == 1:
        global time_record_flag

        if time_record_flag:
            user['loadstarttime'] = datetime.datetime.now()
            time_record_flag = False

        logging.debug(f'icps_differ: {icps_differ}')

        # XXX:数据库中读取最相关的数据，估算当前重量（根据装料时间
        load_level = Sensor.query.order_by(Sensor.id.desc()).first()
        load_level_data = None
        if load_level is None:
            # FIXME: 第一个数据读取不到
            load_level_data = 4440
        else:
            load_level_data = load_level.data
        logging.debug(load_level_data)

        # XXX:基准问题（箱体+轮子
        # 4440: 物位计的高度
        # 1300：轮子高度
        load_level_limit = 4440 - 1300 - box_height*1000 + 60
        # XXX:从数据库中查料高(三堆0，1，2)
        load_level_height0 = 800
        # XXX:确认limit和height0的大小关系
        # XXX:确认装的是第几堆（根据装料点判断

        # 前装车点装料控制程序
        def load_control0(): 
            logging.debug('control0')
            logging.debug(f'control0 -> user[icps_differ]: {user["icps_differ"]}')
            if user['icps_differ'] == distance_0 : 
                duration = datetime.datetime.now() - user['loadstarttime']
                logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')
                if duration.total_seconds() < 4*60:
                    user['allow_plc_work'] = 1
                    user['flag_load'] = 1
                    user['work_weight_status'] = 1
                    user['work_finish'] = 0
                else:
                    # XXX:保证数据平稳
                    is_smooth = smooth()
                    logging.debug(f'is_smooth: {is_smooth}')

                    load_height = Sensor.query.order_by(Sensor.id.desc()).first()
                    logging.debug(load_height)
                    logging.debug(load_height.data)
                    if is_smooth == False:
                        user['allow_plc_work'] = 0
                        user['flag_load'] = 0
                        user['work_weight_status'] = 1
                        user['work_finish'] = 0
                        user['icps_differ'] = distance_1 if distance_0 != distance_1 else distance_2
                    # 如果当前料高未超过限制，且装料时间小于7分钟，继续装料
                    elif float(int(load_height.data)) > load_level_limit:
                        load_duration = datetime.datetime.now() - user['loadstarttime']
                        if load_duration.total_seconds() < 7*60 :
                            user['allow_plc_work'] = 1
                            user['flag_load'] = 1
                            user['work_weight_status'] = 1
                            user['work_finish'] = 0
                        else:  # 如果料高超过限制或装料时间超过7分钟，停止装料
                            user['allow_plc_work'] = 0
                            user['flag_load'] = 0
                            user['work_weight_status'] = 1
                            user['work_finish'] = 0
                            user['icps_differ'] = distance_1 if distance_0 != distance_1 else distance_2
                    else:
                        user['allow_plc_work'] = 0
                        user['flag_load'] = 0
                        user['work_weight_status'] = 1
                        user['work_finish'] = 0
                        user['icps_differ'] = distance_1 if distance_0 != distance_1 else distance_2


        # 中装车点装料控制程序
        def load_control1():
            logging.debug('control1')
            logging.debug(f'control1 -> user[icps_differ]: {user["icps_differ"]}')
            if user['icps_differ'] == distance_1 :   
                load_height = Sensor.query.order_by(Sensor.id.desc()).first()
                if load_height.data > load_level_limit:
                    user['allow_plc_work'] = 1
                    user['flag_load'] = 1
                    user['work_weight_status'] = 1
                    user['work_finish'] = 0
                else:
                    user['allow_plc_work'] = 0
                    user['flag_load'] = 0
                    user['work_weight_status'] = 1
                    user['work_finish'] = 0                   
                    user['icps_differ']  = distance_2


            # 后装车点装料控制程序
        def load_control2():
            global time_record_flag
            logging.debug('control2')
            logging.debug(f'control2 -> user[icps_differ]: {user["icps_differ"]}')
            if user['icps_differ'] == distance_2 or user['icps_differ'] == distance_1: 
                load_height = Sensor.query.order_by(Sensor.id.desc()).first()
                if load_height.data > load_level_limit:
                    user['allow_plc_work'] = 1
                    user['flag_load'] = 1
                    user['work_weight_status'] = 1
                    user['work_finish'] = 0                    
                else:
                    user['allow_plc_work'] = 0
                    user['flag_load'] = 0
                    user['work_weight_status'] = 2
                    user['work_finish'] = 1                   
                    time_record_flag = True


        logging.debug(f'user[icps_differ]: {user["icps_differ"]}')
        if icps_differ == '0123': # 装料三次的控制程序
            if user['icps_differ'] == distance_0 :
                load_control0()
            elif user['icps_differ'] == distance_1 :
                load_control1()
            elif user['icps_differ'] == distance_2 :
                load_control2()


        elif icps_differ == '0012': # 装料两次的控制程序
            if user['icps_differ'] == distance_0 :
                load_control0()
            # if user['icps_differ'] == distance_1 :
            if user['icps_differ'] == distance_2 :
                load_control2()


        elif icps_differ == '0112': # 装料两次的控制程序
            if user['icps_differ'] == distance_0 :
                load_control0()
            elif user['icps_differ'] == distance_1 :    
                load_control2()


        elif icps_differ == '0001': # 装料一次的控制程序
            if user['icps_differ'] == distance_0 :
                load_control0()
            # if user['icps_differ'] == distance_1 :
            if user['allow_plc_work'] == 0:
                user['work_finish'] = 1
                time_record_flag = True
        
        # TODO:  更新数据库

        result = gen_return_data(
            time = req_time,
            store_id = store_id, 
            loader_id = loader_id,
            operating_stations={
                "truck_id" : user['truck_id'],
                "work_weight_status" : user['work_weight_status'],
                "work-weight_reality" : user['work_weight_reality'],     
                "flag_load" : user['flag_load'],
                "height_load" : user['height_load'],
                "allow_plc_work" : user['allow_plc_work'],
                "work_finish" : user['work_finish'], 
            }    
        )

    elif data_type == 2:
        # TODO: 计算出闸量,修正数据库记录（车牌最近一条数据

        #work_weight_reality = 8.9

        result = gen_return_data(
            time = req_time,
            store_id=store_id,
            loader_id=loader_id,
            operating_stations={
                "truck_id" : user['truck_id'],
                "work_total" : user['work_total'],
            })

    elif data_type == 3:
        # TODO: 返回实时数据

        # allow_work_flag = 1 if session['center_popup_confirm'] else 0
        # allow_plc_work = 1 if session['center_popup_confirm'] else 0

        result = gen_return_data(
            time = req_time,
            store_id=store_id, 
            loader_id=loader_id,
            operating_stations={
                "truck_id": user['truck_id'],
                "work_weight_status": user['work_weight_status'],
                "work_weight_reality": user['work_weight_reality'],
                "flag_load": user['flag_load'],
                "height_load": user['height_load'],
                "allow_plc_work": user['allow_plc_work'],
                "work_finish" : user['work_finish'],
            })

    elif data_type == 4:
        # TODO: 车牌弹窗确认

        truck_id_confirm = session.get('truck_id_popup_confirm', True)
        if not truck_id_confirm:
            # 弹出车牌勘误窗口
            from .socket import truck_id_popup
            truck_id_popup({'img_url': picture_url_request})

            session['truck_id_popup_confirm'] = TRUCK_CONFIRM.get()
            truck_id_confirm = session['truck_id_popup_confirm']

        result = gen_return_data(
            time = req_time,
            store_id=store_id, 
            loader_id=loader_id,
            operating_stations={
                "truck_id" : user['truck_id'],
                "allow_work_flag" : user['allow_work_flag'],
            })


    else:
        result = {'message': '无请求参数 KEY/VALUE 类型'}
    
    return jsonify(result)


# 清除session，测试用
def clear_session(opt=['truck_id_popup_confirm', 'center_popup_confirm']):
    for key in opt:
        del session[key]
    return 'clear session success'

def smooth(): # 判断数据趋势是否平滑
    # 再做一次滤波（四个数据）
    is_smooth = False
    a = 0
    latest_data = Sensor.query.order_by(Sensor.id.desc()).limit(30).all() 
    if len(latest_data) < 30:
        logging.debug('数据不足30条!!')
        return True
    for i in range(len(latest_data) - 2,-1,-1):
        data_differ = latest_data[i].data - latest_data[i+1].data
        # data_differ = (latest_data[i+4].data - latest_data[i].data)/4
        if abs(data_differ) < 270 : 
            a += 1
    if a == 29:
        logging.debug('30s前到此刻数据平滑下降')
        is_smooth = True
    else:
        logging.debug('数据存在波动,无法使用')
    return is_smooth

def weight_estimate(time_difference): # 预估重量
    start_load_time = Traffic.query.filter_by(Traffic.truckid).first()
    stop_load_time = Traffic.query.filter_by(Traffic.truckid).first()
    all_weight = Traffic.query.filter_by(Traffic.truckid).first()
    load_time = (start_load_time.loadtime1 - stop_load_time.loadtime2).total_seconds()
    logging.debug(load_time)
    per_second_weight = float(all_weight.loadcurrent) / load_time
    current_load_weight = per_second_weight * time_difference
    return current_load_weight