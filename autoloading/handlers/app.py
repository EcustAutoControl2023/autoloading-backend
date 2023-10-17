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

# 生成返回值
def gen_return_data(
        store_id: int=1,
        loader_id: int=20,
        operating_stations: dict={},
    ):
    global default_os
    # 服务器返回时间
    # res_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    # osi中缺失的值使用默认值填充
    res_os = default_os.copy()
    res_os.update(operating_stations)
    # 返回json格式
    return {
        # "time": res_time,
        "store_id": store_id,
        "loader_id": loader_id,
        "operating_stations": res_os,
    }

#@app.route('/connect',methods=['POST'])
def connect():
    global TRUCK_CONFIRM
    data = request.get_json()
    data_type = data.get('data_type')
    req_time = data.get('time')
    operating_stations = data.get('operating_stations')
    job_id = operating_stations.get('job_id') 
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
    truck_weight_out = 0 if (truck_weight_out is None) or (len(truck_weight_out) == 0) else truck_weight_out
    goods_type = operating_stations.get('goods_type') 
    store_id = operating_stations.get('store_id') 
    loader_id = operating_stations.get('loader_id') 
    flag_operate = operating_stations.get('flag_operate') 
    allow_work_flag = operating_stations.get('allow_work_flag') 
    allow_plc_work = operating_stations.get('allow_plc_work') 
    picture_url_plate = operating_stations.get('picture_url_plate', 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')
    picture_url_request = operating_stations.get('picture_url_request','https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')


    # insert_truck_content(req_time,
    #                     truck_id,  
    #                     truck_load,
    #                     load_current,
    #                     truck_weight_in,
    #                     truck_weight_out,
    #                     goods_type,
    #                     store_id,
    #                     loader_id
    # ) #数据存储到数据库中


    if data_type == 0:
        # TODO: 接收到客户端请求，计算并发送装车策略

        work_total = 1
        work_weight_list = [10,10]

        insert_truck_content(
            req_time=req_time,
            truck_id=truck_id,
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
            work_total=work_total,
            load_level_height1=0,
            load_level_height2=0,
            load_time1=datetime.datetime.now(),
            load_time2=datetime.datetime.now()
        )

        result = gen_return_data(
            store_id=store_id, 
            loader_id=loader_id,
            operating_stations={
                "allow_work_flag": allow_work_flag,
                "work_total": work_total,
                "work_weight_list": work_weight_list,
            })
        


    elif data_type == 1:
        # TODO: 请求允许作业

        # XXX: 中控确认标志，默认不弹窗
        truck_id_confirm = session.get('center_popup_confirm', True)

        if not truck_id_confirm:
            # 弹出物料确认窗口
            from .socket import center_popup
            center_popup({'img_url': picture_url_request})
            logging.info("等待确认弹窗")
            session['center_popup_confirm'] = TRUCK_CONFIRM.get()
            logging.info('完成确认')
            truck_id_confirm = session['center_popup_confirm']
            # XXX:补充（去数据库查找类似批次数据
            # 中控确认，允许作业
            allow_work_flag = 1 if truck_id_confirm else 0 #车牌号正确，允许作业；否则不允许
            allow_plc_work = 1 if truck_id_confirm else 0 #车牌号正确，启动PLC；否则停止
            # 获取开始送料时的时间
            user['loadstarttime'] = datetime.datetime.now()
            result = gen_return_data(
                store_id=store_id, 
                loader_id=loader_id,
                operating_stations={
                    "work_total": 1,
                    "work_weight_list": [10,10],
                    "allow_work_flag": allow_work_flag,
                    "allow_plc_work": allow_plc_work,
                    "work_weight_status": work_weight_status,
                    "flag_load": flag_load,
                })
            return jsonify(result)
        else:
            allow_work_flag = 1 if truck_id_confirm else 0 #车牌号正确，允许作业；否则不允许
            allow_plc_work = 1 if truck_id_confirm else 0 #车牌号正确，启动PLC；否则停止

        if allow_work_flag == 1:
            # 发送信号，控制系统开始送料、下料
            # TODO: 物位计数据读取和计算 以及判断任务是否完成
            # user = Traffic.query.filter_by(truckid = truck_id, loadcurrent = truck_load, goodstype = goods_type).first()
            # time1 = user.loadstarttime
            # time2 = user.loadstoptime
            # time1_obj = datetime.strptime(user[],'%Y-%m-%d %H:%M:%S')
            # time2_obj = datetime.strptime(time2,'%Y-%m-%d %H:%M:%S')
            # time_consume = time2_obj - time1_obj
            #print(f"预计装料耗时{time_consume}秒")

            # XXX:数据库中读取最新数据
            load_level = Sensor.query.order_by(Sensor.id.desc()).first()
            logging.debug(load_level)
            
            # XXX:基准问题（箱体+轮子
            # 4400: 物位计的高度
            # 1000：轮子高度
            # 200： 裕度
            load_level_limit = 4400 - 1000 - box_height*1000 + 200
            # XXX:从数据库中查料高
            load_level_height1 = 800
            # XXX:确认limit和height1的大小关系
            # XXX:确认是height1还是height2
            if load_level.data > load_level_height1:
                work_weight_status = 1
                flag_load = 1
            elif load_level_height1 > load_level.data > load_level_limit:
                # 获取开始送料时的时间
                user['loadendtime'] = datetime.datetime.now()
                # XXX:更新数据库
                work_weight_status = 2 #0  #作业执行情况：0 未开始 1 正在执行 2 已完成 3 检测溢出被动完成
                flag_load = 1 #0  # 装料机状态：0 未装车 1 装车中 2 故障
            else:
                # 获取开始送料时的时间
                user['loadendtime'] = datetime.datetime.now()
                # 第三种情况，大于limit
                work_weight_status = 3 #0  #作业执行情况：0 未开始 1 正在执行 2 已完成 3 检测溢出被动完成
                flag_load = 1 #0  # 装料机状态：0 未装车 1 装车中 2 故障

            if work_weight_status == 2 or work_weight_status == 3:
                # 作业完成，发送信号，取消先前的中控确认，控制系统停止送料、下料
                flag_load = 0
                allow_plc_work = 0
                allow_work_flag = 0
                session['center_popup_confirm'] = False

                data_stop_time = datetime.datetime.now() # 获取停止送料时的时间

            result = gen_return_data(
                store_id=store_id, 
                loader_id=loader_id,
                operating_stations={
                    "work_total": 1,
                    "work_weight_list": [10,10],
                    "allow_work_flag": allow_work_flag,
                    "allow_plc_work": allow_plc_work,
                    "work_weight_status": work_weight_status,
                    "flag_load": flag_load,
            })
            # FIXME:数据存储到数据库中
            # insert_truck_content(
            #     req_time=req_time,
            #     truck_id=truck_id,
            #     truck_load=truck_load,
            #     load_current=load_current,
            #     box_length=box_length,
            #     box_width=box_width,
            #     box_height=box_height,
            #     truck_weight_in=truck_weight_in,
            #     truck_weight_out=truck_weight_out,
            #     goods_type=goods_type,
            #     store_id=store_id,
            #     loader_id=loader_id,
            #     load_level_height1=load_level_height1,
            #     load_level_height2=load_level_height1, # FIXME: 二次装车物位计取值
            #     load_time1=user['loadstarttime'], # FIXME: 第一次装车用时
            #     load_time2=user['loadendtime'], # FIXME: 第二次装车用时
            #     work_total=work_total
            # )
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
        # TODO: 计算出闸量,修正数据库记录（车牌最近一条数据

        work_weight_reality = 8.9
        result = gen_return_data(
            store_id=store_id,
            loader_id=loader_id,
            operating_stations={
                "work_weight_reality": work_weight_reality,
            })

    elif data_type == 3:
        # TODO: 返回实时数据

        # allow_work_flag = 1 if session['center_popup_confirm'] else 0
        # allow_plc_work = 1 if session['center_popup_confirm'] else 0

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

        truck_id_confirm = session.get('truck_id_popup_confirm', True)
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
                'truck_id': truck_id,
            })


    else:
        result = {'message': '无请求参数 KEY/VALUE 类型'}
    
    return jsonify(result)


# 清除session，测试用
def clear_session(opt=['truck_id_popup_confirm', 'center_popup_confirm']):
    for key in opt:
        del session[key]
    return 'clear session success'