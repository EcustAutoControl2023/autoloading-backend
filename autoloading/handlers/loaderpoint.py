import datetime
import logging
from operator import and_
import socket
from flask import jsonify, session
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
        212, 212, 212, 212,
        212, 212, 212, 212,
    ]
    StackposList = [
        "401A", "402A", "403A",
        "401B", "402B", "403B",
        "501A", "502A", "503A",
        "501B", "502B", "503B",
        "601A", "602A", "603A", "604A",
        "601B", "602B", "603B", "604B",
    ]

    def __init__(self, loader_id:str):
        self.Sensor = LoadPoint.SensorList[LoadPoint.loader_index_dict[loader_id]]
        self.server_ip = LoadPoint.ServerList[LoadPoint.loader_index_dict[loader_id]]
        self.hex_data='01040A1100022216'#发送给物位计的命令
        self.byte_data = bytes.fromhex(self.hex_data)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
        self.s.setblocking(False)
        # self.req_time   = datetime.datetime.now()
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
        self.load_current1 = None      # 前装车点总重量
        self.load_current2 = None   # 中装车点总重量
        self.load_current3 = None      # 后装车点总重量
        self.icps_differ_num = None      # 车辆作业策略
        self.icps_differ = ""            # 车辆引导目标位置 
        self.icps_differ_new = []           # 返回的引导位置
        self.icps_flag = 0             # 判断装料情况
        #self.icps_length = len(icps_differ)
        self.load_start_time = datetime.datetime.now()      # 车辆开始装料时间
        self.load_end_time = datetime.datetime.now()        # 车辆结束装料时间
        self.allow_plc_work = 0          # PLC启停控制；0：停止，1：启动
        self.allow_work_flag = None      # 
        self.flag_load = 0               # 装料机状态；0：未装车，1：装车中，2：故障
        self.work_weight_status = 0      # 作业执行情况；0：未开始，1：正在执行，2：已完成，3：检测溢出，被动完成 
        self.work_weight_reality = None  # 作业装料情况(当前装料量)
        self.work_finish = 1             # 任务是否完成，0：未完成，1：完成
        self.time_record_flag = True
        self.insert_traffic_flag = True
        self.height_load = None          # 需要返回给请求方的实时料高
        self.goods_type = ""
        self.work_total = 0             # 当前任务装料总次数
        self.load_current = None      # 本次装载量(任务装载量)


        # XXX: 定义装料高度上限
        self.load_level_limit1 = 3.9      # 第一次装料高度限制
        self.load_level_limit2 = 3.8       # 第二次装料高度限制
        self.load_level_limit3 = 3.75       # 第三次装料高度限制
        self.load_height = SensorData(-1)               # 实时装料高度

        self.load_level_height1 = None         # 第一次装料时高度
        self.load_level_height2 = None         # 第二次装料时高度
        self.load_level_height3 = None         # 第三次装料时高度

        self.load_time1 = None           # 第一次装料所用时间
        self.load_time2 = None           # 第二次装料所用时间
        self.load_time3 = None           # 第三次装料所用时间

        self.loadestimate = None         # 装料预估重量
        self.truck_weight_out = 0        # 合作方给出场重量

        self.five_seconds_ago = datetime.timedelta(seconds=5)      # 物位计滞后时差
        self.logging = create_logger(f'装料点-{loader_id}') # 装料点日志

        self.jobid = 0  # 任务ID编号
        self.loadstatus = '未装车'
        self.location = LoadPoint.LocationList[LoadPoint.loader_index_dict[loader_id]]
        self.stackpos = LoadPoint.StackposList[LoadPoint.loader_index_dict[loader_id]]

    def load_control(self,
                     req_time, data_type,
                     truck_id, truck_load, box_length, box_width, box_height,
                     truck_weight_in, truck_weight_out,
                     goods_type, store_id, loader_id,
                     load_current,temp_manual_stop,
                     distance0, distance1, distance2, icps_differ_current,
                     picture_url_plate, picture_url_request, jobid):
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
        self.load_current   = load_current
        self.goods_type     = goods_type
        self.truck_weight_out = truck_weight_out
        self.jobid          = jobid
        self._weight_in     = truck_weight_in
        self.temp_manual_stop = temp_manual_stop
        #self.logging.debug(f'load_current:{self.load_current}')
        

        # if(self.distance_0 != None):
        #     self.icps_differ.append(self.distance_0)
        # if(self.distance_1 != None): 
        #     self.icps_differ.append(self.distance_1)
        # if(self.distance_2 != None):
        #     self.icps_differ.append(self.distance_2)
        # self.icps_length = len(self.icps_differ)


        if self.data_type == 0:  # 接收任务信息并发送引导策略
            self.logging.debug("data_type:0")
            # TODO: 接收到客户端请求，计算并发送装车策略
            if (self.distance_0 != self.distance_1) and (self.distance_0 != self.distance_2) and (self.distance_1 != self.distance_2):
                self.work_total = 3
                self.work_finish = 0
                self.icps_differ_num = '0123' # 共装车三次，三个装车点各不相同
                self.icps_differ = self.distance_0
                self.icps_differ_new = [self.distance_0, self.distance_1, self.distance_2] # 接口新要求
            elif (self.distance_0 == self.distance_1) and (self.distance_1 != self.distance_2) :
                self.work_total = 2
                self.work_finish = 0
                self.icps_differ_num = '0012' # 共装车两次，前装车点和中装车点相同
                self.icps_differ = self.distance_0
                self.icps_differ_new = [self.distance_0, self.distance_2]
            elif (self.distance_1 == self.distance_2) and (self.distance_1 != self.distance_0) :
                self.work_total = 2
                self.work_finish = 0
                self.icps_differ_num = '0112' # 共装车两次，中装车点和后装车点相同
                self.icps_differ = self.distance_0
                self.icps_differ_new = [self.distance_0, self.distance_1]
            elif (self.distance_0 == self.distance_1) and (self.distance_1== self.distance_2) :
                self.work_total = 1
                self.work_finish = 0
                self.icps_differ_num = '0001' # 共装车一次，三个装车点相同
                self.icps_differ = self.distance_0
                self.icps_differ_new = [self.distance_0]
            else:
                #反馈的icps_differ为空，且work_finish=1，标识任务完成
                self.work_total = 0
                self.icps_differ_num = None # 无装车策略
                self.work_finish = 1
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
                    load_level_height1=0,
                    load_level_height2=0,
                    load_level_height3=0,
                    load_start_time=datetime.datetime.now(),
                    load_time1=datetime.datetime.now(),
                    load_time2=datetime.datetime.now(),
                    load_time3=datetime.datetime.now(),
                    load_estimate=0,
                    jobid=self.jobid,
                    loadstatus=self.loadstatus,
                    location=self.location,
                    stackpos=self.stackpos,
                    load_height=0,
                    loadpoint1=self.distance_0,
                    loadpoint2=self.distance_1,
                    loadpoint3=self.distance_2,
                    load_end_time=self.load_end_time
                )

            # 如果引导策略反馈的 icps_differ 为空，且 work_finish=1，标识任务完成
            self.work_finish = 1 if (self.icps_differ_num is None) and (self.work_finish == 1) else self.work_finish

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
            self.logging.debug("data_type:1")
            self.logging.debug(f"temp_manual_stop: {self.temp_manual_stop}")
            self.logging.debug(f"icps_differ_current: {icps_differ_current}")
            if icps_differ_current != None:
                self.icps_differ = icps_differ_current
            # self.logging.debug(f"temp_manual_stop == False: {self.temp_manual_stop == False}")
            # self.logging.debug(f"temp_manual_stop == 0: {self.temp_manual_stop == 0}")
            # self.logging.debug(f"temp_manual_stop == 1: {self.temp_manual_stop == 1}")


            if(self.temp_manual_stop!=0):
                if(self.icps_differ_num == '0001'):   
                    self.work_finish = 1
                elif(self.icps_differ_num == '0012') or (self.icps_differ_num == '0112'):  
                    if(self.icps_differ == self.distance_0):
                        self.work_finish = 0
                    else:
                        self.work_finish = 1
                elif(self.icps_differ_num == '0123'):
                    if(self.icps_differ == self.distance_0) or (self.icps_differ == self.distance_1):
                        self.work_finish = 0
                    else:
                        self.work_finish = 1

                # FIXME:如果切换手动，是否可以认为此条数据作废？
                if self.work_finish:
                    self.insert_traffic_flag = True
                    self.time_record_flag = True

                return self.stop(self.truck_id,self.loader_id)
            
            # 记录开始装料时间
            if self.time_record_flag:
                self.load_start_time = datetime.datetime.now()
                self.time_record_flag = False
                update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "load_start_time": self.load_start_time,
                        "loadpoint1" : self.distance_0,
                        "loadpoint2" : self.distance_1,
                        "loadpoint3" : self.distance_2,
                    }
                )

            self.logging.debug(f'icps_differ_num: {self.icps_differ_num}')
            self.logging.debug(f'icps_differ: {self.icps_differ}')

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
                        # self.loadcurrent1 = self.load_current      # 获取前装料点装料重量

                elif self.icps_differ == self.distance_1 : # 判断车辆引导位置，执行相应装料点控制程序
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
                        # self.loadcurrent2 = self.load_current      # 获取中装料点装料重量

                elif self.icps_differ == self.distance_2 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control2()
                    # self.logging.debug(f'load_current:{self.load_current}')
                    self.height_load = self.load_height.data
                    # 将PLC状态和任务状态发送至前端

                    # 记录第三个装车点料高和时间
                    if self.work_finish:
                        self.logging.debug("记录装车时间3")
                        self.icps_flag = 0
                        self.load_level_height3 = self.load_height.data  # 获取后装料点装料完成高度
                        self.load_time3 = datetime.datetime.now()  # 获取后装料点装料完成时间
                        # self.loadcurrent3 = self.load_current      # 获取后装料点装料重量


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
                        # self.loadcurrent1 = self.load_current

                if self.icps_differ == self.distance_2 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control2()
                    # self.logging.debug(f'load_current:{self.load_current}')
                    self.height_load = self.load_height.data

                    # 记录第二个装车点料高和时间
                    if self.work_finish:
                        self.icps_flag = 0
                        self.logging.debug("记录装车时间2")
                        self.load_level_height2 = self.load_height.data
                        self.load_time2 = datetime.datetime.now()
                        # self.loadcurrent3 = self.load_current


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
                        # self.loadcurrent1 = self.load_current

                elif self.icps_differ == self.distance_1 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control2()
                    # self.logging.debug(f'load_current:{self.load_current}')
                    self.height_load = self.load_height.data

                    # 记录第二个装车点料高和时间
                    if self.work_finish:
                        self.logging.debug("记录装车时间2")
                        self.icps_flag = 0
                        self.load_level_height2 = self.load_height.data
                        self.load_time2 = datetime.datetime.now()
                        # self.loadcurrent3 = self.load_current


            elif self.icps_differ_num == '0001': # 装料一次的控制程序
                if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control0()
                    # self.logging.debug(f'load_current:{self.load_current}')
                    self.height_load = self.load_height.data
                if self.allow_plc_work == 0:
                    self.work_finish = 1
                    self.load_end_time = datetime.datetime.now()
                    self.time_record_flag = True
                    self.insert_traffic_flag = True
                    # 记录第一个装车点料高和时间
                    self.load_level_height1 = self.load_height.data
                    self.load_time1 = datetime.datetime.now()
                    # self.loadcurrent1 = self.load_current
            else:
                self.logging.debug("无装车策略")
                self.load_height = self.get_sensor_data()
                self.logging.debug(self.load_height.data)




            control_status_socket({'value':self.allow_plc_work,'loaderid':self.loader_id})
            loader_status_socket({'value':self.work_finish,
                                            'loaderid':self.loader_id})

            self.loadstatus = '装车中' if self.work_finish == 0 else '未装车'
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
                        "load_time1": self.load_time1,
                        "load_time2": self.load_time2,
                        "load_time3": self.load_time3,
                        "loadestimate": self.loadestimate,
                        "loadheight": self.load_height.data, #FIXME
                        "loadstatus": self.loadstatus,
                        "loadcurrent1":self.load_current1,
                        "loadcurrent2":self.load_current2,
                        "loadcurrent3":self.load_current3,
                        "goodstype": self.goods_type,
                        "loadendtime": self.load_end_time
                    }
                )
            else:
                update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "loadheight": self.load_height.data,
                        "loadstatus": self.loadstatus
                    }
                )

            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id,
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "work_weight_status" : self.work_weight_status,
                    "work_weight_reality" : self.work_weight_reality,
                    "flag_load" : self.flag_load,
                    "height_load" : self.height_load,
                    "allow_plc_work" : self.allow_plc_work,
                    "work_finish" : self.work_finish,
                }
            )

        elif data_type == 2:
            self.logging.debug("data_type:2")
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
            # # TODO: 返回实时数据
            self.logging.debug("data_type:3")
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
            return result


        elif data_type == 4:
            # TODO: 车牌弹窗确认
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



    def load_control0(self):

        self.logging.debug('control0')
        self.logging.debug(f'control0 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_0 :
            duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')

            if duration.total_seconds() < 1*60:  # 前一分钟持续装料
                current_time = datetime.datetime.now()
                self.load_height = self.get_sensor_data()
                self.logging.debug(f'load_height:{self.load_height.data}')
                self.allow_plc_work = 1        # PLC启动
                self.flag_load = 1             # 装料机装车中
                self.work_weight_status = 1    # 作业正在执行
                self.work_finish = 0           # 任务未完成
            else:
                current_time = datetime.datetime.now()
                self.load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
                if self.sensor_status_ok(load_height=self.load_height) is not True: # 物位计异常，无数据，程序停止
                    self.logging.debug("物位计无数据")
                    return
                self.logging.debug(self.load_height.data)
                if self.load_height.data < self.load_level_limit1 : # 如果料高未超过限制，继续装料
                    self.allow_plc_work = 1
                    self.flag_load = 1
                    self.work_weight_status = 1
                    self.work_finish = 0
                else:  # 如果料高超过限制，停止装料
                    self.allow_plc_work = 0        # PLC停止
                    self.flag_load = 0             # 装料机未装车
                    self.work_weight_status = 2    # 作业已完成
                    self.work_finish = 0           # 任务未完成
                    self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2

            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,duration.total_seconds()) # 估算当前装料量
            self.logging.debug(f'loadestimate:{self.loadestimate}')
            


    # 中装车点装料控制程序
    def load_control1(self):

        self.logging.debug('control1')
        self.logging.debug(f'control1 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_1 :

            duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')
            self.load_height = self.get_sensor_data()
            self.logging.debug(f'load_height:{self.load_height.data}')


            if self.load_height.data < self.load_level_limit2: # 如果料高未超过限制，继续装料
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0
            else:
                self.allow_plc_work = 0
                self.flag_load = 0
                self.work_weight_status = 2
                self.work_finish = 0
                self.icps_differ  = self.distance_2

            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,duration.total_seconds()) # 估算当前装料量
            self.logging.debug(f'loadestimate:{self.loadestimate}')



    # 后装车点装料控制程序
    def load_control2(self):

        self.logging.debug('control2')
        self.logging.debug(f'control2 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_2 or self.icps_differ == self.distance_1:
            duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')
            self.load_height = self.get_sensor_data()
            self.logging.debug(f'load_height:{self.load_height.data}')

            if self.load_height.data < self.load_level_limit3: # 如果料高未超过限制，继续装料
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0
            else:
                self.allow_plc_work = 0
                self.flag_load = 0
                self.work_weight_status = 2
                self.work_finish = 1
                self.load_end_time = datetime.datetime.now()  # 获取任务结束时间
                self.time_record_flag = True
                self.insert_traffic_flag = True

            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,duration.total_seconds()) # 估算当前装料量
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
            return SensorData(load_height.data)

    # 预估重量
    def weight_estimate(self, goods_type,loader_id,time_difference):
        current_load_weight = 0.0  # 当前载重量
        per_second_weight = 0
        #筛选数据, 注意需要去除当前正在装车的数据
        filtered_traffic = Traffic.query.filter(and_(Traffic.loaderid==loader_id,Traffic.goodstype==goods_type)).all()[:-1]
        # self.logging.debug(f'\033[31mfiltered_traffic: {filtered_traffic}\033[0m')
        self.logging.debug(f'filtered_traffic: {filtered_traffic}')
        # 没有数据直接退出

        #提取筛选后数据的某一属性
        start_load_times = [traffic.loadstarttime for traffic in filtered_traffic if traffic.loadstarttime is not None]
        stop_load_times = [traffic.loadendtime for traffic in filtered_traffic if traffic.loadendtime is not None]

        loader_weight_in = [traffic.truckweightin for traffic in filtered_traffic if traffic.truckweightin is not None]  # 车辆进场重量
        loader_weight_out = [traffic.truckweightout for traffic in filtered_traffic if traffic.truckweightout is not None]  # 车辆出场重量

        loader_weight_total = [(weight_out - weight_in) for weight_in, weight_out in zip(loader_weight_in, loader_weight_out)]  # 车辆装载净重
        self.logging.debug(f'loader_weight_total: {loader_weight_total}')


        #计算装载时间
        load_time = [(stop - start).total_seconds() for start, stop in zip(start_load_times, stop_load_times)]  # 每一次任务的总装载时间
        # print(f'\033[31mload_time: {load_time}\033[0m')
        self.logging.debug(f'load_time: {load_time}')

        filtered_data_length = min(len(load_time),len(loader_weight_total))
        self.logging.debug(f'filtered_data_length: {filtered_data_length}')

        # print(f'\033[31mfiltered_data_length: {filtered_data_length}\033[0m')
        # print(f'\033[31mloader_task_len: {len(loader_task)}\033[0m')
        if filtered_data_length == 0:
            return None

        for i in range(filtered_data_length):
            try:
                # print(f'\033[31mloadtime: {load_time[i]}\033[0m')
                # print(f'\033[31mloadtask: {loader_task[i]}\033[0m')
                per_second_weight += loader_weight_total[i] / load_time[i] * 1.0
            except ZeroDivisionError:
                print('\033[31merror\033[0m')
                return None

        per_second_weight /= filtered_data_length
        current_load_weight = per_second_weight * time_difference

        return current_load_weight
    
    def stop(self, truck_id, loader_id):
        self.allow_plc_work = 0
        # self.work_finish = 0
        self.loadstatus = '未装车'
        self.work_weight_status = 3
        # self.insert_traffic_flag = True
        # self.time_record_flag = True
        self.logging.debug("stop!")
        control_status_socket({'value':self.allow_plc_work,'loaderid':self.loader_id})
        loader_status_socket({'value':self.work_finish,'loaderid':self.loader_id})
        self.logging.debug(f'truckid: {truck_id}')
        result = gen_return_data(
            time = self.req_time,
            store_id = self.store_id,
            loader_id = self.loader_id,
            operating_stations={
                "truck_id" : self.truck_id,
                "allow_plc_work" : self.allow_plc_work,
                "work_finish" : self.work_finish,
                "work_weight_status": self.work_weight_status
            }
        )

        return result




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
