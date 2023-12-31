import datetime
import logging
from autoloading.config import TRUCK_CONFIRM
from flask import jsonify, session
from autoloading.handlers.truck_store import insert_truck_content, update_truck_content
from autoloading.models.sensor import Traffic, loader_num
for i in range(loader_num):
    exec(f'from autoloading.models.sensor import Sensor{i+1}')

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


# 生成返回值
def gen_return_data(
        time,
        store_id: int=1,
        loader_id: int=20,
        operating_stations: dict={},
    ):

    res_os = dict()
    res_os.update(operating_stations)
    # 返回json格式
    return {
        "time": time,
        "store_id": store_id,
        "loader_id": loader_id,
        "operating_stations": res_os,
    }

class LoadPoint:
    # XXX:定义装料点的id列表
    loader_id_list = [i for i in range(loader_num)]
    # 定义装料点的index列表
    loader_index_list = [i for i in range(loader_num)]
    loader_index_dict = dict(zip(loader_id_list, loader_index_list))
    logging.debug(f'loader_index_dict: {loader_index_dict}')
    # 定义类变量SensorList, 用于存储每个Sensor类
    SensorList = list()
    for i in range(loader_num):
        exec(f'SensorList.append(Sensor{i+1})')
    def __init__(self, loader_id:int):
        self.Sensor = LoadPoint.SensorList[LoadPoint.loader_index_dict[loader_id]]
        self.req_time = datetime.datetime.now()
        self.truck_id = ''
        self.truck_load = 0
        self.data_type = -1
        self.store_id = 0
        self.loader_id = 0
        self.distance_0 = 0
        self.distance_1 = 0
        self.distance_2 = 0
        self.icps_differ_num = None
        self.icps_differ = ''
        self.load_start_time = datetime.datetime.now()
        self.allow_plc_work = 0
        self.allow_work_flag = None
        self.flag_load = 0
        self.work_weight_status = 0
        self.work_weight_reality = None
        self.work_finish = 0
        self.time_record_flag = True
        self.height_load = None

    def load_control(self,
                     req_time, data_type,
                     truck_id, truck_load, box_length, box_width, box_height,
                     truck_weight_in, truck_weight_out,
                     goods_type, store_id, loader_id,
                     load_current, 
                     distance0, distance1, distance2,
                     picture_url_plate, picture_url_request):
        self.req_time = req_time
        self.data_type = data_type
        self.truck_id = truck_id
        self.truck_load = truck_load
        self.store_id = store_id
        self.loader_id = loader_id
        self.distance0 = distance0
        self.distance1 = distance1
        self.distance2 = distance2

        if self.data_type == 0:

            # TODO: 接收到客户端请求，计算并发送装车策略
            if (self.distance_0 != self.distance_1) and (self.distance_0 != self.distance_2) and (self.distance_1 != self.distance_2):
                self.work_total = 3
                self.icps_differ_num = '0123' # 共装车三次，三个装车点各不相同
                self.icps_differ = self.distance_0
            elif self.distance_0 == self.distance_1 and self.distance_1 != self.distance_2 :
                self.work_total = 2
                self.icps_differ_num = '0012' # 共装车两次，前装车点和中装车点相同
                self.icps_differ = self.distance_0
            elif self.distance_1 == self.distance_2 and self.distance_1 != self.distance_0 :
                self.work_total = 2
                self.icps_differ_num = '0112' # 共装车两次，中装车点和后装车点相同
                self.icps_differ = self.distance_0
            elif self.distance_0 == self.distance_1 == self.distance_2 :
                self.work_total = 1
                self.icps_differ_num = '0001' # 共装车一次，三个装车点相同
                self.icps_differ = self.distance_0
            else:
                self.work_total = 0
                self.icps_differ_num = None # 无装车策略
                self.work_finish = 1
            
            logging.debug(f'icps_differ: {self.icps_differ_num}')

            insert_truck_content(
                req_time=self.req_time,
                truck_id=self.truck_id,
                truck_load=self.truck_load,
                box_length=box_length,
                box_width=box_width,
                box_height=box_height,
                truck_weight_in=truck_weight_in,
                truck_weight_out=truck_weight_out,
                goods_type=goods_type,
                store_id=store_id,
                loader_id=self.loader_id,
                load_current=load_current,
                work_total=self.work_total,
                load_level_height1=0,
                load_level_height2=0,
                load_time1=datetime.datetime.now(),
                load_time2=datetime.datetime.now()
            )

            # 如果引导策略反馈的 icps_differ 为空，且 work_finish=1，标识任务完成
            self.work_finish = 0 if (self.icps_differ_num is None) and (self.work_finish == 1) else self.work_finish

            # user['icps_differ'] = icps_differ
            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id, 
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "icps_differ" : self.icps_differ_num,

                })
        elif data_type == 1:

            if self.time_record_flag:
                self.load_start_time = datetime.datetime.now()
                self.time_record_flag = False

            logging.debug(f'icps_differ: {self.icps_differ_num}')

            # XXX:数据库中读取最相关的数据，估算当前重量（根据装料时间
            load_level = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
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

            logging.debug(f'icps_differ: {self.icps_differ}')
            if self.icps_differ_num == '1113': # 装料三次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                elif self.icps_differ == self.distance_1 :
                    self.load_control1()
                elif self.icps_differ == self.distance_2 :
                    self.load_control2()

            elif self.icps_differ_num == '0012': # 装料两次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                # if user['icps_differ'] == distance_1 :
                if self.icps_differ == self.distance_2 :
                    self.load_control2()

            elif self.icps_differ_num == '1002': # 装料两次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                elif self.icps_differ == self.distance_1 :    
                    self.load_control2()

            elif self.icps_differ_num == '0001': # 装料一次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                # if user['icps_differ'] == distance_1 :
                if self.allow_plc_work == 0:
                    self.work_finish = 1
                    self.time_record_flag = True
            
            # TODO:  更新数据库
            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id, 
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "work_weight_status" : self.work_weight_status,
                    "work-weight_reality" : self.work_weight_reality,     
                    "flag_load" : self.flag_load,
                    "height_load" : self.height_load,
                    "allow_plc_work" : self.allow_plc_work,
                    "work_finish" : self.work_finish, 
                }    
            )

        elif data_type == 2:
            # TODO: 计算出闸量,修正数据库记录（车牌最近一条数据

            #work_weight_reality = 8.9

            result = gen_return_data(
                time = self.req_time,
                store_id=self.store_id,
                loader_id=self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "work_total" : self.work_total,
                })

        elif data_type == 3:
            # TODO: 返回实时数据

            # allow_work_flag = 1 if session['center_popup_confirm'] else 0
            # allow_plc_work = 1 if session['center_popup_confirm'] else 0

            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id, 
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id": self.truck_id,
                    "work_weight_status": self.work_weight_status,
                    "work_weight_reality": self.work_weight_reality,
                    "flag_load": self.flag_load,
                    "height_load": self.height_load,
                    "allow_plc_work": self.allow_plc_work,
                    "work_finish" : self.work_finish,
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
                time = self.req_time,
                store_id = self.store_id, 
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "allow_work_flag" : self.allow_work_flag,
                })


        else:
            result = {'message': '无请求参数 KEY/VALUE 类型'}
        
        return jsonify(result)


    def smooth(self):
        # 再做一次滤波（四个数据）
        is_smooth = False
        a = 0
        latest_data = self.Sensor.query.order_by(self.Sensor.id.desc()).limit(30).all() 
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

    # 预估重量
    def weight_estimate(time_difference): 

        start_load_time = Traffic.query.filter_by(Traffic.truckid).first()
        stop_load_time = Traffic.query.filter_by(Traffic.truckid).first()
        all_weight = Traffic.query.filter_by(Traffic.truckid).first()
        load_time = (start_load_time.loadtime1 - stop_load_time.loadtime2).total_seconds()
        logging.debug(load_time)
        per_second_weight = float(all_weight.loadcurrent) / load_time
        current_load_weight = per_second_weight * time_difference
        return current_load_weight

    def load_control0(self): 

        logging.debug('control0')
        logging.debug(f'control0 -> icps_differ: {self.icps_differ}')
        if self.icps_differ == self.distance_0 : 
            duration = datetime.datetime.now() - self.load_start_time
            logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')
            if duration.total_seconds() < 4*60:
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0
            else:
                # XXX:保证数据平稳
                is_smooth = self.smooth()
                logging.debug(f'is_smooth: {is_smooth}')
                load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
                logging.debug(load_height)
                logging.debug(load_height.data)
                if is_smooth == False:
                    self.allow_plc_work = 0
                    self.flag_load = 0
                    self.work_weight_status = 1
                    self.work_finish = 0
                    self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2
                # 如果当前料高未超过限制，且装料时间小于7分钟，继续装料
                elif float(int(load_height.data)) > self.load_level_limit:
                    load_duration = datetime.datetime.now() - self.load_start_time
                    if load_duration.total_seconds() < 7*60 :
                        self.allow_plc_work = 1
                        self.flag_load = 1
                        self.work_weight_status = 1
                        self.work_finish = 0
                    else:  # 如果料高超过限制或装料时间超过7分钟，停止装料
                        self.allow_plc_work = 0
                        self.flag_load = 0
                        self.work_weight_status = 1
                        self.work_finish = 0
                        self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2
                else:
                    self.allow_plc_work = 0
                    self.flag_load = 0
                    self.work_weight_status = 1
                    self.work_finish = 0
                    self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2

    # 中装车点装料控制程序
    def load_control1(self):

        logging.debug('control1')
        logging.debug(f'control1 -> icps_differ: {self.icps_differ}')
        if self.icps_differ == self.distance_1 :   
            load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
            if load_height.data > self.load_level_limit:
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0
            else:
                self.allow_plc_work = 0
                self.flag_load = 0
                self.work_weight_status = 1
                self.work_finish = 0                   
                self.icps_differ  = self.distance_2

    # 后装车点装料控制程序
    def load_control2(self):
        logging.debug('control2')
        logging.debug(f'control2 -> icps_differ: {self.icps_differ}')
        if self.icps_differ == self.distance_2 or self.icps_differ == self.distance_1: 
            load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
            if load_height.data > self.load_level_limit:
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0                    
            else:
                self.allow_plc_work = 0
                self.flag_load = 0
                self.work_weight_status = 2
                self.work_finish = 1                   
                self.time_record_flag = True

