import datetime
import logging
from datetime import timedelta
from queue import Queue
import socket
from flask import jsonify, session
from sqlalchemy import False_
from autoloading.handlers.truck_store import insert_truck_content, update_truck_content
from autoloading.models.sensor import Traffic, loader_num
from .socket import control_status_socket,loader_status_socket
from autoloading.config import create_logger

for i in range(loader_num):
    exec(f'from autoloading.models.sensor import Sensor{i+1}')


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

class SensorData:
    '''
    物位计数据类
    '''
    def __init__(self, data:float):
        self.data = data

class LoadPoint:
    # 定义装料点的id列表 [1-20]
    loader_id_list = [
        "401A", "402A", "403A",
        "401B", "402B", "403B",
        "501A", "502A", "503A",
        "501B", "502B", "503B",
        "601A", "602A", "603A", "604A",
        "601B", "602B", "603B", "604B",
    ]
    # 定义装料点的index列表
    loader_index_list = [i for i in range(loader_num)]
    loader_index_dict = dict(zip(loader_id_list, loader_index_list))
    # logging.debug(f'loader_index_dict: {loader_index_dict}')
    # 定义类变量SensorList, 用于存储每个Sensor类
    SensorList = list()
    for i in range(loader_num):
        exec(f'SensorList.append(Sensor{i+1})')
    ServerList = [('172.16.175.59',8234),('172.16.175.65',8234),('172.16.175.71',8234),('172.16.175.77',8234),
                  ('172.16.175.83',8234),('172.16.175.89',8234),('172.16.175.95',8234),('172.16.175.101',8234),
                  ('172.16.175.107',8234),('172.16.175.113',8234),('172.16.175.119',8234),('172.16.175.125',8234),
                  ('172.16.175.131',8234),('172.16.175.137',8234),('172.16.175.143',8234),('172.16.175.149',8234),
                  ('172.16.175.155',8234),('172.16.175.161',8234),('172.16.175.167',8234),('172.16.175.173',8234)] #物位计的ip地址、端口号
    LocationList = [
        212, 212, 212,
        212, 212, 212,
        212, 212, 212,
        212, 212, 212,
        213, 213, 213, 213,
        213, 213, 213, 213,
    ]
    StackposList = [
        "401A", "402A", "403A",
        "401B", "402B", "403B",
        "501A", "502A", "503A",
        "501B", "502B", "503B",
        "601A", "602A", "603A", "604A",
        "601B", "602B", "603B", "604B",
    ]
    LoadCoefficient = {
        "黄豆": [(9.5, 10.5), 10, 9],
        "油菜籽": [(9, 9.8), 9.8, 9]
    }

    def __init__(self, loader_id:str):
        self.Sensor = LoadPoint.SensorList[LoadPoint.loader_index_dict[loader_id]]
        self.server_ip = LoadPoint.ServerList[LoadPoint.loader_index_dict[loader_id]]
        self.hex_data='01040A1100022216'#发送给物位计的命令
        self.byte_data = bytes.fromhex(self.hex_data)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
        self.s.setblocking(False)

        self.req_time   = None  # 任务开始时间
        self.task_finish_time = None # 任务完成时间

        self.truck_id   = ''       # 车牌信息
        self.truck_load = 0        # 车辆最大载重
        self.data_type  = -1       # 数据类型，0：请求作业策略；1：请求允许作业；2：出闸重量；3：请求实时作业情况数据；4：识别有误弹窗确认
        self.store_id   = 0        # 装料仓库编号
        self.loader_id  = 0        # 装料机编号
        self.box_length = 0        # 箱体长
        self.box_width  = 0        # 箱体宽
        self.box_height = 0        # 箱体高
        self.distance_0 = None        # 车辆前装车点距离
        self.distance_1 = None        # 车辆中装车点距离
        self.distance_2 = None        # 车辆后装车点距离
        self.icps_differ_num = None      # 车辆作业策略
        self.icps_differ = ""            # 车辆引导目标位置 
        self.icps_differ_new = []           # 返回的引导位置
        self.icps_flag = 0             # 判断装料情况
        self.load_start_time = datetime.datetime.now()      # 车辆开始装料时间
        self.load_end_time = None        # 车辆结束装料时间
        self.allow_plc_work = 0          # PLC启停控制；0：停止，1：启动
        self.allow_work_flag = None      # 
        self.flag_load = 0               # 装料机状态；0：未装车，1：装车中，2：故障
        self.work_weight_status = 0      # 作业执行情况；0：未开始，1：正在执行，2：已完成，3：检测溢出，被动完成 
        # self.work_weight_reality = None  # 作业装料情况(当前装料量)
        self.work_finish = 0             # 任务是否完成，0：未完成，1：完成
        self.time_record_flag = True     # 时间记录标志
        self.insert_traffic_flag = False   # 判断是否是新任务
        self.height_load = None          # 需要返回给请求方的实时料高
        self.goods_type = ""             # 货物类型
        self.work_total = 0             # 当前任务装料总次数
        self.load_current = 0      # 本次装载量(任务装载量)
        self.loading_state = None     # 下料状态，true：下料中，false停止下料
        self.type_of_opening = None    # 开口类型
        self.opening_length_bias = 0    # 侧边距
        self.opening_width_bias = 0      # 尾边距
        self.opening_length = 0          # 开口长
        self.opening_width = 0            # 开口宽


        # XXX: 定义装料高度上限
        self.load_level_limit1 = 3.7 #3.72      # 第一次装料高度限制
        self.load_level_limit2 = 3.7 #3.65       # 第二次装料高度限制
        self.load_level_limit3 = 3.7 #3.65       # 第三次装料高度限制
        self.load_height = SensorData(-1)               # 实时装料高度
        self.load_height1_begin = 0           # 新增，第1堆初始高度
        self.load_height2_begin = 0           # 新增，第2堆初始高度
        self.load_height3_begin = 0           # 新增，第3堆初始高度
        self.load_weight1_end = 0                  # 新增，第1堆结束重量
        self.load_weight2_end = 0                  # 新增，第2堆结束重量
        self.load_height_queue = Queue(maxsize=10) # 新增，最近10条高度（队列）
        self.load_height_list = list()             # 新增，最近10条高度（list）

        self.load_level_height1 = None         # 第一次装料时高度
        self.load_level_height2 = None         # 第二次装料时高度
        self.load_level_height3 = None         # 第三次装料时高度

        self.load_time1 = None           # 第一次装料完成时间
        self.load_time2 = None           # 第二次装料完成时间
        self.load_time3 = None           # 第三次装料完成时间
        self.load_time = datetime.timedelta(0)            # 装料所用时间
        self.load_start_time1_flag = True   #中装料点时间记录控制标志
        self.load_start_time2_flag = True   #后装料点时间记录控制标志

        self.loadestimate = 0         # 装料预估重量
        self.truck_weight_out = 0        # 合作方给出场重量

        self.duration = float(0)                    #装料持续时间

        # self.five_seconds_ago = datetime.timedelta(seconds=5)      # 物位计滞后时差
        self.logging = create_logger(f'装料点-{loader_id}') # 装料点日志

        self.jobid = 0  # 任务ID编号
        self.loadstatus = '未装车'
        self.location = LoadPoint.LocationList[LoadPoint.loader_index_dict[loader_id]]
        self.stackpos = LoadPoint.StackposList[LoadPoint.loader_index_dict[loader_id]]

    # TODO: 函数输入参数改为字典
    def load_control(self,
                     req_time, data_type,
                     truck_id, truck_load, box_length, box_width, box_height,
                     truck_weight_in, truck_weight_out,
                     goods_type, store_id, loader_id,
                     load_current,temp_manual_stop,
                     distance0, distance1, distance2, icps_differ_current,
                     picture_url_plate, picture_url_request, jobid,loading_state,
                     type_of_opening,opening_length_bias,opening_width_bias,
                     opening_length,opening_width,
                     breakdowncode,emergency_stop,auto_select,belt_motor_run):

        self.req_time       = datetime.datetime.now() 
        self.data_type      = data_type
        self.truck_id       = truck_id
        self.truck_load     = truck_load
        self.store_id       = store_id
        self.loader_id      = loader_id
        self.box_length     = box_length
        self.box_width      = box_width
        self.box_height     = box_height
        self.distance_0     = distance0
        self.distance_1     = distance1
        self.distance_2     = distance2
        self.load_current   = load_current - 1.5  # 保守装，少2吨，临时调整
        self.goods_type     = goods_type
        self.truck_weight_out = truck_weight_out
        self.jobid          = jobid
        self._weight_in     = truck_weight_in
        self.temp_manual_stop = temp_manual_stop
        self.loading_state = loading_state
        self.type_of_opening = type_of_opening
        self.opening_length_bias = opening_length_bias
        self.opening_width_bias = opening_width_bias
        self.opening_length = opening_length
        self.opening_width = opening_width
        self.breakdowncode = breakdowncode
        self.emergency_stop = emergency_stop
        self.auto_select = auto_select
        self.belt_motor_run = belt_motor_run

        if self.data_type == 0:  # 接收任务信息并发送引导策略
            self.logging.debug("data_type:0")
            self.logging.debug(f"truck_id:{self.truck_id}开始任务")

            traffic = Traffic.query.filter_by(loaderid=self.loader_id).order_by(Traffic.id.desc()).first()
            self.logging.debug(f'traffic: {traffic}')
            # 判断是否有新车辆到达, 如果有新车辆到达，初始化装料点状态
            if traffic is None or (traffic.truckid != self.truck_id):
                self.logging.debug(f"新装料任务：{self.truck_id}")
                self.work_finish = 0
                self.icps_flag = 0
                self.insert_traffic_flag = True
                self.time_record_flag = True
                self.load_start_time1_flag = True
                self.load_start_time2_flag = True
                self.icps_differ = self.distance_0
                self.load_height1_begin = 0
                self.load_height2_begin = 0
                self.load_height3_begin = 0
                self.load_weight1_end = 0
                self.load_weight2_end = 0
                self.load_height_queue = Queue(maxsize=10)
                self.load_height_list = list()
                self.load_height = SensorData(-1)
                self.load_level_limit1 = 0.85 + self.box_height #第一次装料高度限制，1.2为车厢底
                self.load_level_limit2 = 0.85 + self.box_height #第二次装料高度限制
                self.load_level_limit3 = 0.85 + self.box_height #第三次装料高度限制


            if (self.distance_0 != self.distance_1) and (self.distance_0 != self.distance_2) and (self.distance_1 != self.distance_2):
                self.work_total = 3
                self.icps_differ_num = '0123' # 共装车三次，三个装车点各不相同
                self.icps_differ_new = [self.distance_0, self.distance_1, self.distance_2] # 接口新要求
            elif (self.distance_0 == self.distance_1) and (self.distance_1 != self.distance_2) :
                self.work_total = 2
                self.icps_differ_num = '0012' # 共装车两次，前装车点和中装车点相同
                self.icps_differ_new = [self.distance_0, self.distance_2]
            elif (self.distance_1 == self.distance_2) and (self.distance_1 != self.distance_0) :
                self.work_total = 2
                self.icps_differ_num = '0112' # 共装车两次，中装车点和后装车点相同
                self.icps_differ_new = [self.distance_0, self.distance_1]
            elif (self.distance_0 == self.distance_1) and (self.distance_1== self.distance_2) :
                self.work_total = 1
                self.icps_differ_num = '0001' # 共装车一次，三个装车点相同
                self.icps_differ_new = [self.distance_0]
            else:
                # TODO: 无装车策略

                #反馈的icps_differ为空，且work_finish=1，标识任务完成
                self.work_total = 0
                self.icps_differ_num = None # 无装车策略
                self.work_finish = 1
                # self.load_end_time = self.load_start_time + timedelta(seconds=self.duration if self.duration is not None else 0)
                self.load_end_time = datetime.datetime.now()
                self.time_record_flag = True
                self.insert_traffic_flag = True
                self.icps_differ_new = []

            self.logging.debug(f'icps_differ_num: {self.icps_differ_num}')  # 打印装车策略
            # 将数据存入数据库中, 仅在每个装车任务开始时，插入一条新的记录
            self.logging.debug(f'self.insert_traffic_flag: {self.insert_traffic_flag}')
            if self.insert_traffic_flag:
                self.insert_traffic_flag = False
                insert_truck_content(  
                    req_time=self.req_time,
                    truck_id=self.truck_id,
                    truck_load=self.truck_load,
                    box_length=self.box_length,
                    box_width=self.box_width,
                    box_height=self.box_height,
                    truck_weight_in=truck_weight_in,
                    truck_weight_out=truck_weight_out,
                    goods_type=goods_type,
                    store_id=store_id,
                    loader_id=self.loader_id,
                    load_current=self.load_current,
                    work_total=self.work_total,
                    load_start_time=datetime.datetime.now(),
                    jobid=self.jobid,
                    loadstatus=self.loadstatus,
                    location=self.location,
                    stackpos=self.stackpos,
                    load_height=0,
                    loadpoint1=self.distance_0,
                    loadpoint2=self.distance_1,
                    loadpoint3=self.distance_2,
                    type_of_opening = self.type_of_opening,
                    opening_length_bias = self.opening_length_bias,
                    opening_width_bias = self.opening_width_bias,
                    opening_length = self.opening_length,
                    opening_width = self.opening_width,
                    load_time = 0
                )

            # 如果引导策略反馈的 icps_differ 为空，且 work_finish=1，标识任务完成
            # self.work_finish = 1 if (self.icps_differ_num is None) and (self.work_finish == 1) else self.work_finish
            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id,
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "icps_differ" : self.icps_differ_new[self.icps_flag:],
                    "work_finish" : self.work_finish
                })

        elif data_type == 1:  # 车辆引导到位，发送PLC控制策略
            self.logging.debug(f"{self.truck_id}请求data_type:1")
            self.logging.debug(f"temp_manual_stop: {self.temp_manual_stop}")
            self.logging.debug(f"loading_state: {self.loading_state}")
            self.logging.debug(f"icps_differ_current: {icps_differ_current}")
            if icps_differ_current != None:
                self.icps_differ = icps_differ_current

            # self.logging.debug(f"loading_state:{self.loading_state}")
            # self.logging.debug(f"loading_state==false:{self.loading_state==0}")
            if(self.loading_state == 0):

                self.allow_plc_work = 0
                result = gen_return_data(
                    time = self.req_time,
                    store_id = self.store_id,
                    loader_id = self.loader_id,
                    operating_stations={
                        "truck_id" : self.truck_id,
                        "allow_plc_work" : self.allow_plc_work,
                        "work_finish" : self.work_finish,
                        "work_weight_status": self.work_weight_status,
                        "loading_state":self.loading_state
                    }
                )

                return result

            # 记录开始装料时间
            if self.time_record_flag:
                self.load_start_time = datetime.datetime.now()
                self.logging.debug(f"load_start_time: {self.load_start_time}")
                self.duration = float(0)
                self.time_record_flag = False
                update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "load_start_time": self.load_start_time,
                    }
                )
                # 记录初始高度，第1堆料开始前
                if self.load_height1_begin == 0:
                    self.load_height1_begin = self.get_sensor_data().data
                    if 1.3 < self.load_height1_begin < 2.5:  # 如果扫描到底部加强筋，强制赋值
                        self.load_height1_begin = 1.2
                    elif self.load_height1_begin < 0:
                        self.load_height1_begin = 0 
                    elif self.load_height1_begin > 3.5: # 如果扫描到的是顶部的加强筋，不装料，不估计重量
                        pass
                    update_truck_content(
                        truckid=self.truck_id,
                        loaderid=self.loader_id,
                        update_data={
                            "loadheight1begin": self.load_height1_begin,
                        }
                    )

            if(self.temp_manual_stop!=0):
                self.logging.debug("手动停止")
                self.logging.debug(f"icps_differ_num:{self.icps_differ_num}")
                self.logging.debug(f"icps_differ:{self.icps_differ}")
                self.logging.debug(f'distance_0:{self.distance_0}')
                self.logging.debug(f'distance_1:{self.distance_1}')
                self.logging.debug(f'distance_2:{self.distance_2}')
                self.load_height = self.get_sensor_data()
                if(self.icps_differ_num == '0001'):   
                    self.work_finish = 1
                    self.load_time1 = datetime.datetime.now()
                    assert type(self.load_start_time) == datetime.datetime
                    # self.duration = (self.load_time1 - self.load_start_time).total_seconds()
                    self.logging.debug("前装料点装料完毕,记录装料时间1")
                    self.load_level_height1 = self.load_height.data  # 获取前装料点装料完成高度
                elif(self.icps_differ_num == '0012') or (self.icps_differ_num == '0112'):  
                    if(self.icps_differ == self.distance_0):
                        self.work_finish = 0
                        self.load_time1 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        self.load_time = datetime.datetime.now() - self.load_start_time # 更新当前装料所用时间
                        assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time1 - self.load_start_time).total_seconds()
                        self.icps_differ = self.distance_2
                        self.logging.debug("前装料点装料完毕,记录装料时间1")
                        self.load_level_height1 = self.load_height.data  # 获取前装料点装料完成高度
                    else:
                        self.work_finish = 1
                        self.load_time2 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time2 - self.load_start_time).total_seconds()
                        self.logging.debug("后装料点装料完毕,记录装料时间2")
                        self.load_level_height2 = self.load_height.data  # 获取前装料点装料完成高度
                elif(self.icps_differ_num == '0123'):
                    if(self.icps_differ == self.distance_0):
                        self.work_finish = 0
                        self.load_time1 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        self.load_time = datetime.datetime.now() - self.load_start_time # 更新当前装料所用时间

                        # self.duration = (self.load_time1 - self.load_start_time).total_seconds()
                        self.icps_differ = self.distance_1
                        self.logging.debug("前装料点装料完毕,记录装料时间1")
                        self.load_level_height1 = self.load_height.data  # 获取前装料点装料完成高度

                    elif(self.icps_differ == self.distance_1):
                        self.load_time2 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time2 - self.load_start_time).total_seconds()
                        self.icps_differ = self.distance_2

                        # self.load_time += datetime.datetime.now() - self.load_start_time1 # 更新当前装料所用时间


                        self.logging.debug("中装料点装料完毕,记录装料时间2")
                        self.load_level_height2 = self.load_height.data  # 获取前装料点装料完成高度

                    else:
                        self.work_finish = 1
                        self.load_time3 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time3 - self.load_start_time).total_seconds()
                        self.logging.debug("后装料点装料完毕,记录装料时间3")
                        self.load_level_height3 = self.load_height.data  # 获取前装料点装料完成高度

                # FIXME:如果切换手动，是否可以认为此条数据作废？
                if self.work_finish:
                    self.icps_flag += 1

                return self.stop(self.truck_id,self.loader_id)

            self.logging.debug(f'icps_differ_num: {self.icps_differ_num}')
            self.logging.debug(f'icps_differ: {self.icps_differ}')

            if self.work_finish == 0:
                if self.duration > 1500 :
                    self.time_record_flag = True
                    self.insert_traffic_flag = True
                    return None
                if self.icps_differ_num == '0123': # 装料三次的控制程序
                    if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                        self.load_control0() # 执行前装料点控制程序
                        # self.logging.debug(f'load_current:{self.load_current}')  # 打印当前装载重量(第一次无数据)

                        self.height_load = self.load_height.data 
                        # self.logging.debug(f'load_height.data: {self.load_height.data}')
                        # 记录第一个装车点料高和时间
                        if self.icps_differ == self.distance_1:
                            self.icps_flag = 1  # 第一堆料装料完成，需要引导
                            self.logging.debug("前装料点装料完毕,记录装料时间1")
                            self.load_level_height1 = self.load_height.data  # 获取前装料点装料完成高度
                            self.load_time1 = datetime.datetime.now()  # 获取前装料点装料完成时间
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height1": self.load_level_height1,
                                }
                            )
                        if self.work_finish:
                            self.logging.debug("记录装车时间")
                            self.icps_flag += 1
                            self.load_level_height1 = self.load_height.data  # 获取后装料点装料完成高度
                            self.load_time1 = datetime.datetime.now()  # 获取后装料点装料完成时间
                            assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
                            self.load_end_time = datetime.datetime.now()
                            self.load_weight1_end = self.loadestimate
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height1": self.load_level_height1,
                                }
                            )
                    elif self.icps_differ == self.distance_1 : # 判断车辆引导位置，执行相应装料点控制程序
                        if self.load_height2_begin == 0:
                            self.load_height_queue = Queue(maxsize=10)
                            self.load_height_list = list()
                            self.load_height2_begin = self.get_sensor_data().data
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "loadheight2begin": self.load_height2_begin,
                                }
                            )
                        self.icps_flag = 1
                        self.load_control1()
                        # self.logging.debug(f'load_current:{self.load_current}')
                        self.height_load = self.load_height.data       # 获取当前料高
                        # 将PLC状态和任务状态发送至前端
                        # 记录第二个装车点料高和时间
                        if self.icps_differ == self.distance_2:
                            self.icps_flag = 2
                            self.logging.debug("中装料点装料完毕,记录装车时间2")
                            self.load_level_height2 = self.load_height.data  # 获取中装料点装料完成高度
                            self.load_time2 = datetime.datetime.now()  # 获取中装料点装料完成时间
                            self.load_weight2_end = self.loadestimate
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height2": self.load_level_height2,
                                }
                            )
                        if self.work_finish:
                            self.logging.debug("记录装车时间")
                            self.icps_flag += 1
                            self.load_level_height2 = self.load_height.data  # 获取后装料点装料完成高度
                            self.load_time2 = datetime.datetime.now()  # 获取后装料点装料完成时间
                            assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
                            self.load_end_time = datetime.datetime.now()
                            
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height2": self.load_level_height2,
                                }
                            )
                    elif self.icps_differ == self.distance_2 : # 判断车辆引导位置，执行相应装料点控制程序
                        if self.load_height3_begin == 0:
                            self.load_height_queue = Queue(maxsize=10)
                            self.load_height_list = list()
                            self.load_height3_begin = self.get_sensor_data().data
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "loadheight3begin": self.load_height3_begin,
                                }
                            )
                        self.icps_flag = 2
                        self.load_control2()
                        # self.logging.debug(f'load_current:{self.load_current}')
                        self.height_load = self.load_height.data
                        # 将PLC状态和任务状态发送至前端

                        # 记录第三个装车点料高和时间
                        if self.work_finish:
                            self.logging.debug("记录装车时间3")
                            self.icps_flag += 1
                            self.load_level_height3 = self.load_height.data  # 获取后装料点装料完成高度
                            self.load_time3 = datetime.datetime.now()  # 获取后装料点装料完成时间
                            assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
                            self.load_end_time = self.load_start_time + timedelta(seconds=self.duration)
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height3": self.load_level_height3,
                                }
                            )
                elif self.icps_differ_num == '0012': # 装料两次的控制程序
                    if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                        self.load_control0()
                        # self.logging.debug(f'load_current:{self.load_current}')
                        self.height_load = self.load_height.data
                        # 记录第一个装车点料高和时间
                        if self.icps_differ == self.distance_2:
                            self.logging.debug("记录装车时间1")
                            self.icps_flag = 1
                            self.load_level_height1 = self.load_height.data
                            self.load_time1 = datetime.datetime.now()
                            self.load_weight1_end = self.loadestimate
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height1": self.load_level_height1,
                                }
                            )
                    elif self.icps_differ == self.distance_2 : # 判断车辆引导位置，执行相应装料点控制程序
                        if self.load_height2_begin == 0:
                            self.load_height_queue = Queue(maxsize=10)
                            self.load_height_list = list()
                            self.load_height2_begin = self.get_sensor_data().data
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "loadheight2begin": self.load_height2_begin,
                                }
                            )
                        self.icps_flag = 1
                        self.load_control2()
                        # self.logging.debug(f'load_current:{self.load_current}')
                        self.height_load = self.load_height.data

                        # 记录第二个装车点料高和时间
                        if self.work_finish:
                            self.logging.debug("记录装车时间2")
                            self.icps_flag += 1
                            self.load_level_height2 = self.load_height.data
                            self.load_time2 = datetime.datetime.now()
                            assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
                            self.load_end_time = self.load_start_time + timedelta(seconds=self.duration)

                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height2": self.load_level_height2,
                                }
                            )
                elif self.icps_differ_num == '0112': # 装料两次的控制程序
                    if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                        self.load_control0()
                        # self.logging.debug(f'load_current:{self.load_current}')
                        self.height_load = self.load_height.data
                        # 记录第一个装车点料高和时间
                        if self.icps_differ == self.distance_1:
                            self.icps_flag = 1
                            self.logging.debug("记录装车时间1")
                            self.load_level_height1 = self.load_height.data
                            self.load_time1 = datetime.datetime.now()
                            self.load_weight1_end = self.loadestimate
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height1": self.load_level_height1,
                                }
                            )
                    elif self.icps_differ == self.distance_1 : # 判断车辆引导位置，执行相应装料点控制程序
                        if self.load_height2_begin == 0:
                            self.load_height_queue = Queue(maxsize=10)
                            self.load_height_list = list()
                            self.load_height2_begin = self.get_sensor_data().data
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "loadheight2begin": self.load_height2_begin,
                                }
                            )
                        self.icps_flag = 1
                        self.load_control2()
                        # self.logging.debug(f'load_current:{self.load_current}')
                        self.height_load = self.load_height.data

                        # 记录第二个装车点料高和时间
                        if self.work_finish:
                            self.logging.debug("记录装车时间2")
                            self.icps_flag += 1
                            self.load_level_height2 = self.load_height.data
                            assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
                            self.load_end_time = self.load_start_time + timedelta(seconds=self.duration)
                            self.load_time2 = datetime.datetime.now()
                            # 更新数据库
                            update_truck_content(
                                truckid=self.truck_id,
                                loaderid=self.loader_id,
                                update_data={
                                    "load_level_height2": self.load_level_height2,
                                }
                            )
                elif self.icps_differ_num == '0001': # 装料一次的控制程序
                    if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                        self.load_control0()
                        # self.logging.debug(f'load_current:{self.load_current}')
                        self.height_load = self.load_height.data
                    if self.allow_plc_work == 0:
                        self.work_finish = 1
                        self.icps_flag += 1
                        assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
                        self.load_end_time = self.load_start_time + timedelta(seconds=self.duration)
                        # self.time_record_flag = True
                        # self.insert_traffic_flag = True
                        # 记录第一个装车点料高和时间
                        self.load_level_height1 = self.load_height.data
                        self.load_time1 = datetime.datetime.now()
                else:
                    self.logging.debug("无装车策略")
                    self.load_height = self.get_sensor_data()
                    self.logging.debug(self.load_height.data)

                self.loadstatus = '装车中' if self.work_finish == 0 else '装车完成'
                if self.work_finish:
                    # 更新数据库
                    update_truck_content(
                        truckid=self.truck_id,
                        loaderid=self.loader_id,
                        update_data={
                            "truck_weight_out": self.truck_weight_out,
                            "load_level_height1": self.load_level_height1,
                            "load_level_height2": self.load_level_height2,
                            "load_level_height3": self.load_level_height3,
                            "loadestimate": self.loadestimate,
                            "loadheight": self.load_height.data,
                            "loadstatus": self.loadstatus,
                            "goodstype": self.goods_type,
                            "loadendtime": self.load_end_time,
                            "loadtimetotal": self.load_time.total_seconds()
                        }
                    )
                    self.load_end_time = None
                else:
                    update_truck_content(
                        truckid=self.truck_id,
                        loaderid=self.loader_id,
                        update_data={
                            "loadheight": self.load_height.data,
                            "loadstatus": self.loadstatus
                        }
                    )

            control_status_socket({'value':self.allow_plc_work,'loaderid':self.loader_id})
            loader_status_socket({'value':self.work_finish,'loaderid':self.loader_id})

            self.logging.debug(f"[type1]work_finish:{self.work_finish}")
            self.logging.debug(f"[type1]loadstatus:{self.loadstatus}")
            self.logging.debug(f"[type1]allow_plc_work:{self.allow_plc_work}")
            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id,
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "work_weight_status" : self.work_weight_status,
                    "work_weight_reality" : self.loadestimate,
                    "flag_load" : self.flag_load,
                    "height_load" : self.height_load,
                    "allow_plc_work" : self.allow_plc_work,
                    "work_finish" : self.work_finish,
                }
            )

        elif data_type == 2:
            self.logging.debug(f"{self.truck_id}请求data_type:2")
            update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "truck_weight_out": self.truck_weight_out,
                    }
                )
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
            self.logging.debug(f"{self.truck_id}请求data_type:3")
            self.logging.debug(f"auto_select:{self.auto_select}")

            if self.auto_select == False:
                self.logging.debug("手动停止")
                self.logging.debug(f"icps_differ_num:{self.icps_differ_num}")
                self.logging.debug(f"icps_differ:{self.icps_differ}")
                self.logging.debug(f'distance_0:{self.distance_0}')
                self.logging.debug(f'distance_1:{self.distance_1}')
                self.logging.debug(f'distance_2:{self.distance_2}')
                self.load_height = self.get_sensor_data()
                if(self.icps_differ_num == '0001'):   
                    self.work_finish = 1
                    self.load_time1 = datetime.datetime.now()
                    assert type(self.load_start_time) == datetime.datetime
                    # self.duration = (self.load_time1 - self.load_start_time).total_seconds()
                    self.logging.debug("前装料点装料完毕,记录装料时间1")
                    self.load_level_height1 = self.load_height.data  # 获取前装料点装料完成高度
                elif(self.icps_differ_num == '0012') or (self.icps_differ_num == '0112'):  
                    if(self.icps_differ == self.distance_0):
                        self.work_finish = 0
                        self.load_time1 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        self.load_time = datetime.datetime.now() - self.load_start_time # 更新当前装料所用时间
                        assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time1 - self.load_start_time).total_seconds()
                        self.icps_differ = self.distance_2
                        self.logging.debug("前装料点装料完毕,记录装料时间1")
                        self.load_level_height1 = self.load_height.data  # 获取前装料点装料完成高度
                    else:
                        self.work_finish = 1
                        self.load_time2 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time2 - self.load_start_time).total_seconds()
                        self.logging.debug("后装料点装料完毕,记录装料时间2")
                        self.load_level_height2 = self.load_height.data  # 获取前装料点装料完成高度
                elif(self.icps_differ_num == '0123'):
                    if(self.icps_differ == self.distance_0):
                        self.work_finish = 0
                        self.load_time1 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        self.load_time = datetime.datetime.now() - self.load_start_time # 更新当前装料所用时间

                        # self.duration = (self.load_time1 - self.load_start_time).total_seconds()
                        self.icps_differ = self.distance_1
                        self.logging.debug("前装料点装料完毕,记录装料时间1")
                        self.load_level_height1 = self.load_height.data  # 获取前装料点装料完成高度

                    elif(self.icps_differ == self.distance_1):
                        self.load_time2 = datetime.datetime.now()
                        assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time2 - self.load_start_time).total_seconds()
                        self.icps_differ = self.distance_2

                        # self.load_time += datetime.datetime.now() - self.load_start_time1 # 更新当前装料所用时间


                        self.logging.debug("中装料点装料完毕,记录装料时间2")
                        self.load_level_height2 = self.load_height.data  # 获取前装料点装料完成高度

                    else:
                        self.work_finish = 1
                        self.load_time3 = datetime.datetime.now()
                        # assert type(self.load_start_time) == datetime.datetime
                        # self.duration = (self.load_time3 - self.load_start_time).total_seconds()
                        self.logging.debug("后装料点装料完毕,记录装料时间3")
                        self.load_level_height3 = self.load_height.data  # 获取前装料点装料完成高度

                # FIXME:如果切换手动，是否可以认为此条数据作废？
                if self.work_finish:
                    self.icps_flag += 1

                self.stop(self.truck_id,self.loader_id)

            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id,
                loader_id = self.loader_id,
                operating_stations={
                    # "truck_id": self.truck_id,
                    # "work_weight_status": self.work_weight_status,
                    "work_weight_reality": self.loadestimate,
                    # "flag_load": self.flag_load,
                    "height_load": self.height_load,
                    # "allow_plc_work": self.allow_plc_work,
                    # "work_finish" : self.work_finish,
                })
            return result


        elif data_type == 4:
            from autoloading.config import TRUCK_CONFIRM
            self.logging.debug("data_type:4")
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

    def update_weightout(self, 
                         distance_0, distance_1, distance_2,
                         truck_id, loader_id, req_time, store_id,
                         truck_weight_out):
        self.logging.debug(f"{truck_id}data_type:2")
        self.logging.debug(f"truck_weight_out:{truck_weight_out}")
        if (distance_0 != distance_1) and (distance_0 != distance_2) and (distance_1 != distance_2):
            work_total = 3
        elif (distance_0 == distance_1) and (distance_1 != distance_2) :
            work_total = 2
        elif (distance_1 == distance_2) and (distance_1 != distance_0) :
            work_total = 2
        elif (distance_0 == distance_1) and (distance_1== distance_2) :
            work_total = 1
        else:
            work_total = 0
        update_truck_content(
                truckid=truck_id,
                loaderid=loader_id,
                update_data={
                    "truck_weight_out": truck_weight_out,
                }
            )
        return gen_return_data(
            time = req_time,
            store_id=store_id,
            loader_id=loader_id,
            operating_stations={
                "truck_id" : truck_id,
                "work_total" : work_total,
            })

    def load_control0(self):
        self.logging.debug(f'control0 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_0 :
            assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
            self.duration = (datetime.datetime.now() - self.load_start_time).total_seconds()  # 计算装料持续时间
            self.logging.debug(f'load_control0 -> duration:{self.duration}')
            self.load_height = self.get_sensor_data()
            self.logging.debug(f'load_height:{self.load_height.data}')
            # self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,self.duration) # 估算当前装料量
            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,float(self.load_height.data), 1, 0, self.load_height1_begin) # 估算当前装料量
            self.logging.debug(f'loadestimate:{self.loadestimate}')
            if self.duration < 0*60:  # 前一分钟持续装料，改：不强制装料
                self.allow_plc_work = 1        # PLC启动
                self.flag_load = 1             # 装料机装车中
                self.work_weight_status = 1    # 作业正在执行
                self.work_finish = 0           # 任务未完成
            else:
                self.logging.debug(f'load_height:{self.load_height.data}')
                if self.load_height.data < self.load_level_limit1 and self.loadestimate <= self.load_current: # 如果料高/重量未超过限制，继续装料
                    self.allow_plc_work = 1
                    self.flag_load = 1
                    self.work_weight_status = 1
                    self.work_finish = 0
                elif self.loadestimate > self.load_current:
                    self.allow_plc_work = 0
                    self.flag_load = 0
                    self.work_weight_status = 2
                    self.work_finish = 1
                    self.load_time = datetime.datetime.now() - self.load_start_time
                    self.load_end_time = datetime.datetime.now()
                    self.load_start_time2_flag = True
                    self.icps_differ = None
                    self.icps_flag = 2
                    self.logging.debug("重量达到,任务结束")
                else:  # 如果料高超过限制，停止装料
                    self.allow_plc_work = 0        # PLC停止
                    self.flag_load = 0             # 装料机未装车
                    self.work_weight_status = 2    # 作业已完成
                    self.work_finish = 0           # 任务未完成
                    self.load_time = datetime.datetime.now() - self.load_start_time
                    self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2
                    self.logging.debug("前装料点装料完毕")
                    self.load_weight1_end = self.loadestimate


    # 中装车点装料控制程序
    def load_control1(self):
        self.logging.debug(f'control1 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_1 :

            if(self.load_start_time1_flag):
                self.load_start_time1 = datetime.datetime.now()
                self.load_start_time1_flag=False

            # duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.duration = self.load_time.total_seconds() + (datetime.datetime.now() - self.load_start_time1).total_seconds()  # 计算装料持续时间
            self.logging.debug(f'load_control1 -> duration:{self.duration}')


            self.load_height = self.get_sensor_data()
            self.logging.debug(f'load_height:{self.load_height.data}')


            # if self.load_height.data < self.load_level_limit2: # 如果料高未超过限制，继续装料
            # if self.loadestimate < self.load_current :
            if self.load_height.data < self.load_level_limit2 and self.loadestimate < self.load_current: # 如果料高未超过限制，继续装料
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0
            elif self.loadestimate > self.load_current:
                self.allow_plc_work = 0
                self.flag_load = 0
                self.work_weight_status = 2
                self.work_finish = 1
                self.load_time += datetime.datetime.now() - self.load_start_time1
                self.load_end_time = datetime.datetime.now()
                self.load_start_time1_flag = True
                self.icps_differ = None
                self.icps_flag = 2
                self.logging.debug("重量达到,任务结束")
            else:
                self.allow_plc_work = 0         # PLC停止
                self.flag_load = 0              # 装料机未装 
                self.work_weight_status = 2     # 作业已完成
                self.work_finish = 0            # 任务未完成
                self.icps_differ  = self.distance_2
                self.load_time += datetime.datetime.now() - self.load_start_time1
                self.load_start_time1_flag = True
                self.load_weight2_end = self.loadestimate
                self.logging.debug("中装料点装料完毕")


            # self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,self.duration) # 估算当前装料量
            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,float(self.load_height.data), 2, self.load_weight1_end, self.load_height2_begin)
            self.logging.debug(f'loadestimate:{self.loadestimate}')



    # 后装车点装料控制程序
    def load_control2(self):
        self.logging.debug(f'control2 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_2 or self.icps_differ == self.distance_1:

            if(self.load_start_time2_flag):
                self.load_start_time2 = datetime.datetime.now()
                self.load_start_time2_flag=False

            # duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.duration = self.load_time.total_seconds() + (datetime.datetime.now() - self.load_start_time2).total_seconds()  # 计算装料持续时间
            self.logging.debug(f'load_control2 -> duration:{self.duration}')
            

            self.load_height = self.get_sensor_data()
            self.logging.debug(f'load_height:{self.load_height.data}')

            if self.load_height.data < self.load_level_limit3 and self.loadestimate < self.load_current: # 如果料高未超过限制，继续装料
            # if self.load_height.data < self.load_level_limit3: # 如果料高未超过限制，继续装料
            # if self.loadestimate < self.load_current :
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0
            else:
                self.allow_plc_work = 0
                self.flag_load = 0
                self.work_weight_status = 2
                self.work_finish = 1
                assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
                self.load_end_time = self.load_start_time + timedelta(self.duration)  # 获取任务结束时间
                # self.time_record_flag = True
                # self.insert_traffic_flag = True
                self.load_time += datetime.datetime.now() - self.load_start_time2
                self.load_start_time2_flag = True
                self.logging.debug("后装料点装料完毕")

            # self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,self.duration) # 估算当前装料量
            if self.work_total == 2:
                self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,float(self.load_height.data), 2, self.load_weight1_end, self.load_height2_begin)
            else:
                self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,float(self.load_height.data), 3, self.load_weight2_end, self.load_height3_begin)
            self.logging.debug(f'loadestimate:{self.loadestimate}')

    def sensor_status_ok(self, load_height)-> bool:
        if load_height is None:
            self.logging.debug("物位计无数据")
            self.allow_plc_work = 0
            self.work_finish = 0
            return False
        else:
            return True

    def get_sensor_data(self)-> SensorData:
        load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
        if load_height is None:
            self.logging.debug("物位计无数据")
            self.allow_plc_work = 0
            self.work_finish = 0
            return SensorData(-1)
        else:
            load_height = load_height.data
            # 第一堆装料开始后，给第1个物位值，后面的物位值不能小于前一个物位值，如果小于，则物位值等于前一个物位值
            if len(self.load_height_list) != 0 and self.load_height_list[-1] > load_height:
                load_height = self.load_height_list[-1]
            if self.load_height_queue.full():
                self.load_height_queue.get()
            self.load_height_queue.put(load_height)
            self.load_height_list = list(self.load_height_queue.queue)
            return SensorData(load_height)

    # 预估重量：用时间估计
    def weight_estimate_old(self, goods_type,loader_id,time_difference) -> float:
        current_load_weight = 0 # 当前载重量
        per_second_weight = None
        bean_ratio = 0.0434
        corn_ratio = 0.043
        rapeseed_ratio = 0.048 * 1.2  # 0.043

        if goods_type == "黄豆":
            per_second_weight = bean_ratio
        elif goods_type == "玉米":
            per_second_weight = corn_ratio
        elif goods_type == "油菜籽" :
            per_second_weight = rapeseed_ratio

        assert per_second_weight is not None
    
        current_load_weight = per_second_weight * time_difference

        return current_load_weight

    # 预估重量2：用高度估计
    def weight_estimate_v0(self, goods_type,loader_id,load_height, height_num) -> float:
        # height_num，第1，2，3堆
        current_load_weight = 0 # 当前载重量

        if load_height < 1:  # 503南物位计数据上窜下跳
            return 0
        
        if goods_type == "黄豆":
            if height_num==1:
                current_load_weight = 23*(load_height-1.2)/(3.5-1.2)
            elif height_num==2:
                current_load_weight = 23+abs(load_height-3)*5.2/(3.4-3)
            else:
                current_load_weight = 23+abs(load_height-3)*5.2/(3.4-3) # 不对，现场没有第3堆数据
        elif goods_type == "玉米":
            if height_num==1:
                current_load_weight = 23*(load_height-1.2)/(3.5-1.2)
            elif height_num==2:
                current_load_weight = 23+abs(load_height-3)*5.2/(3.4-3)
            else:
                current_load_weight = 23+abs(load_height-3)*5.2/(3.4-3) # 不对，现场没有第3堆数据
        elif goods_type == "油菜籽" :
            if height_num==1:
                current_load_weight = 23*(load_height-1.2)/(3.5-1.2)
            elif height_num==2:
                current_load_weight = 23+abs(load_height-3)*5.2/(3.4-3)
            else:
                current_load_weight = 23+abs(load_height-3)*5.2/(3.4-3) # 不对，现场没有第3堆数据

        return current_load_weight

    # 预估重量2：用高度估计
    def weight_estimate(self, goods_type,loader_id,load_height, height_num, load_weight_begin, load_height_begin) -> float:
        # height_num，第1，2，3堆
        current_load_weight = 0 # 当前载重量
        self.logging.debug(f"[weight_estimate] load_weight_begin:{load_weight_begin}")
        self.logging.debug(f"[weight_estimate] load_height_begin:{load_height_begin}")

        if load_height < 1:  # 503南物位计数据上窜下跳
            return 0
        if height_num == 1:
            co11, co12 = self.LoadCoefficient[goods_type][height_num-1]
            if load_height - load_height_begin < 0.9:
                current_load_weight = co11 * (load_height - load_height_begin)
            elif load_height - load_height_begin >= 0.9:
                current_load_weight = co11 * 0.9 + (load_height - load_height_begin - 0.9) * co12
        elif height_num == 2:
            co2 = self.LoadCoefficient[goods_type][height_num-1]
            current_load_weight = load_weight_begin + (load_height - load_height_begin) * co2
        else:
            co3 = self.LoadCoefficient[goods_type][height_num-1]
            current_load_weight = load_weight_begin + (load_height - load_height_begin) * co3

        return current_load_weight

    def stop(self, truck_id, loader_id):
        self.logging.debug(f'truckid: {truck_id}')
        self.logging.debug(f'loaderid: {loader_id}')
        self.logging.debug("stop!")
        self.allow_plc_work = 0
        # self.work_finish = 1
        self.work_weight_status = 2
        # assert type(self.duration) == float; assert type(self.load_start_time) == datetime.datetime
        self.load_end_time = self.load_start_time + timedelta(seconds=self.duration)
        self.loadstatus = "装车完成"
        # self.insert_traffic_flag = True
        # self.time_record_flag = True
        self.load_start_time1_flag = True
        self.load_start_time2_flag = True
        control_status_socket({'value':self.allow_plc_work,'loaderid':self.loader_id})
        loader_status_socket({'value':self.work_finish,'loaderid':self.loader_id})

        result = gen_return_data(
            time = self.req_time,
            store_id = self.store_id,
            loader_id = self.loader_id,
            operating_stations={
                "truck_id" : self.truck_id,
                "work_weight_status": self.work_weight_status,
                "work_weight_reality": self.loadestimate,
                "flag_load": self.flag_load,
                "height_load": self.height_load,
                "allow_plc_work" : self.allow_plc_work,
                "work_finish" : self.work_finish,
            },
        )
        update_truck_content(
            truckid=self.truck_id,
            loaderid=self.loader_id,
            update_data={
                "loadendtime": self.load_end_time,
                "loadestimate": self.loadestimate,
                "loadstatus": self.loadstatus,
                "loadtimetotal": self.duration,
                "load_level_height1": self.load_level_height1,
                "load_level_height2": self.load_level_height2,
                # "load_level_height3": self.load_level_height3,

            }
        )          
        self.logging.debug(f"loadendtime:{self.load_end_time}")   
        self.logging.debug(f"duration:{self.duration}")   

        # self.insert_traffic_flag = True
        # self.duration = None
        # self.load_end_time = None

        return result

    def reconnectudp(self):
        self.s.close()
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
        self.s.setblocking(False)

    def clearUDPBuffer(self):
        while True:
            try:
                buf = self.s.recv(4096)
            except BlockingIOError as b:
                break


# 将每个装料点定义成一个类的实例
load_point_dict = dict()

def create_loader_points():
    global load_point_dict
    load_point_list = [LoadPoint(i) for i in LoadPoint.loader_id_list]

    # 生成字典
    load_point_dict = dict(zip(LoadPoint.loader_id_list, load_point_list))

if len(load_point_dict) == 0:
    logging.debug("=======================")
    create_loader_points()
