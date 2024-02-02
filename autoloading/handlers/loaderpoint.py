import datetime
import logging
from operator import and_
import socket
from autoloading.config import TRUCK_CONFIRM
from flask import jsonify, session
from autoloading.handlers.truck_store import insert_truck_content, update_truck_content
from autoloading.models import sensor
from autoloading.models.sensor import Traffic, loader_num
from .socket import coontrol_status_socket,loader_status_socket
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

class LoadPoint:
    # 定义装料点的id列表 [1-20]
    loader_id_list = [i+1 for i in range(loader_num)]
    # 定义装料点的index列表
    loader_index_list = [i for i in range(loader_num)]
    loader_index_dict = dict(zip(loader_id_list, loader_index_list))
    logging.debug(f'loader_index_dict: {loader_index_dict}')
    # 定义类变量SensorList, 用于存储每个Sensor类
    SensorList = list()
    for i in range(loader_num):
        exec(f'SensorList.append(Sensor{i+1})')
    ServerList = [('172.16.175.59',8234),('172.16.175.65',8234),('172.16.175.71',8234),('172.16.175.77',8234),
                  ('172.16.175.83',8234),('172.16.175.89',8234),('172.16.175.95',8234),('172.16.175.101',8234),
                  ('172.16.175.107',8234),('172.16.175.113',8234),('172.16.175.119',8234),('172.16.175.125',8234),
                  ('172.16.175.131',8234),('172.16.175.137',8234),('172.16.175.143',8234),('172.16.175.149',8234),
                  ('172.16.175.155',8234),('172.16.175.161',8234),('172.16.175.167',8234),('172.16.175.173',8234)] #物位计的ip地址、端口号

    def __init__(self, loader_id:int):
        self.Sensor = LoadPoint.SensorList[LoadPoint.loader_index_dict[loader_id]]
        self.server_ip = LoadPoint.ServerList[LoadPoint.loader_index_dict[loader_id]]
        self.hex_data='01040A1100022216'#发送给物位计的命令
        self.byte_data = bytes.fromhex(self.hex_data)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# UDP
        self.s.setblocking(False)
        self.req_time   = datetime.datetime.now()
        self.truck_id   = ''       # 车牌信息
        self.truck_load = 0        # 车辆最大载重
        self.data_type  = -1       # 数据类型，0：请求作业策略；1：请求允许作业；2：出闸重量；3：请求实时作业情况数据；4：识别有误弹窗确认
        self.store_id   = 0        # 装料仓库编号
        self.loader_id  = 0        # 装料机编号
        self.box_length = 0        # 箱体长
        self.box_width  = 0        # 箱体宽
        self.box_height = 0        # 箱体高
        self.distance_0 = 0        # 车辆前装车点距离
        self.distance_1 = 0        # 车辆中装车点距离
        self.distance_2 = 0        # 车辆后装车点距离
        self.load_current = 0      # 车辆本次任务装载量
        self.icps_differ_num = None      # 车辆作业策略
        self.icps_differ = ''            # 车辆引导目标位置 
        self.load_start_time = datetime.datetime.now()      # 车辆开始装料时间
        self.load_end_time = datetime.datetime.now()        # 车辆结束装料时间
        self.allow_plc_work = 0          # PLC启停控制；0：停止，1：启动
        self.allow_work_flag = None      # 
        self.flag_load = 0               # 装料机状态；0：未装车，1：装车中，2：故障
        self.work_weight_status = 0      # 作业执行情况；0：未开始，1：正在执行，2：已完成，3：检测溢出，被动完成 
        self.work_weight_reality = None  # 作业装料情况(当前装料量)
        self.work_finish = 1             # 任务是否完成，0：未完成，1：完成
        self.time_record_flag = True
        self.height_load = None
        self.goods_type = ""

        # XXX: 定义装料高度上限
        self.load_level_limit1 = 3.7       # 第一次装料高度限制
        self.load_level_limit2 = 3.6       # 第二次装料高度限制
        self.load_level_limit3 = 3.5       # 第三次装料高度限制
        self.load_height = 0

        self.load_height1 = None         # 第一次装料时高度
        self.load_height2 = None         # 第二次装料时高度
        self.load_height3 = None         # 第三次装料时高度

        self.load_time1 = None           # 第一次装料所用时间
        self.load_time2 = None           # 第二次装料所用时间
        self.load_time3 = None           # 第三次装料所用时间

        self.loadestimate = None         # 装料预估重量
        self.truck_weight_out = 0        # 合作方给出场重量？

        self.five_seconds_ago = datetime.timedelta(seconds=5)      # 物位计滞后时差
        self.logging = create_logger(f'装料点-{loader_id}') # 装料点日志

    def load_control(self,
                     req_time, data_type,
                     truck_id, truck_load, box_length, box_width, box_height,
                     truck_weight_in, truck_weight_out,
                     goods_type, store_id, loader_id,
                     load_current,
                     distance0, distance1, distance2,
                     picture_url_plate, picture_url_request):
        self.req_time       = req_time
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

        if self.data_type == 0:  # 接收任务信息并发送引导策略

            # TODO: 接收到客户端请求，计算并发送装车策略
            if (self.distance_0 != self.distance_1) and (self.distance_0 != self.distance_2) and (self.distance_1 != self.distance_2):
                self.work_total = 3
                self.work_finish = 0
                self.icps_differ_num = '0123' # 共装车三次，三个装车点各不相同
                self.icps_differ = self.distance_0
            elif (self.distance_0 == self.distance_1) and (self.distance_1 != self.distance_2) :
                self.work_total = 2
                self.work_finish = 0
                self.icps_differ_num = '0012' # 共装车两次，前装车点和中装车点相同
                self.icps_differ = self.distance_0
            elif (self.distance_1 == self.distance_2) and (self.distance_1 != self.distance_0) :
                self.work_total = 2
                self.work_finish = 0
                self.icps_differ_num = '0112' # 共装车两次，中装车点和后装车点相同
                self.icps_differ = self.distance_0
            elif (self.distance_0 == self.distance_1) and (self.distance_1== self.distance_2) :
                self.work_total = 1
                self.work_finish = 0
                self.icps_differ_num = '0001' # 共装车一次，三个装车点相同
                self.icps_differ = self.distance_0
            else:
                #反馈的icps_differ为空，且work_finish=1，标识任务完成
                self.work_total = 0
                self.icps_differ_num = None # 无装车策略
                self.work_finish = 1
                self.load_end_time = datetime.datetime.now()
                self.time_record_flag = True

            self.logging.debug(f'icps_differ_num: {self.icps_differ_num}')

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
                load_estimate=0
            )

            # 如果引导策略反馈的 icps_differ 为空，且 work_finish=1，标识任务完成
            self.work_finish = 1 if (self.icps_differ_num is None) and (self.work_finish == 1) else self.work_finish

            result = gen_return_data(
                time = self.req_time,
                store_id = self.store_id,
                loader_id = self.loader_id,
                operating_stations={
                    "truck_id" : self.truck_id,
                    "icps_differ" : self.icps_differ_num,
                    "work_finish" : self.work_finish

                })
        elif data_type == 1:  # 车辆引导到位，发送PLC控制策略

            # 记录开始装料时间
            if self.time_record_flag:
                self.load_start_time = datetime.datetime.now()
                self.time_record_flag = False
                update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "load_start_time": self.load_start_time,
                    }
                )




            # XXX:数据库中读取最相关的数据，估算当前重量（根据装料时间
            # load_level = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
            # load_level_data = None
            # if load_level is None:
            #     # FIXME: 第一个数据读取不到
            #     load_level_data = 4040
            # else:
            #     load_level_data = load_level.data
            # self.logging.debug(load_level_data)

            # XXX:基准问题（箱体+轮子
            # 4440: 物位计的高度
            # 1300：轮子高度
            # self.load_level_limit = 4040 # 4440 - 1300 - box_height*1000 + 60
            # XXX:从数据库中查料高(三堆0，1，2)
            # load_level_height0 = 800
            # XXX:确认limit和height0的大小关系
            # XXX:确认装的是第几堆（根据装料点判断
            self.logging.debug(f'icps_differ_num: {self.icps_differ_num}')
            self.logging.debug(f'icps_differ: {self.icps_differ}')

            if self.icps_differ_num == '0123': # 装料三次的控制程序
                if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control0() # 执行前装料点控制程序
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                    # 记录第一个装车点料高和时间
                    if self.icps_differ == self.distance_1:
                        self.load_height1 = self.load_height.data
                        self.load_time1 = datetime.datetime.now()
                elif self.icps_differ == self.distance_1 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control1()
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                    # 记录第二个装车点料高和时间
                    if self.icps_differ == self.distance_2:
                        self.load_height2 = self.load_height.data
                        self.load_time2 = datetime.datetime.now()
                elif self.icps_differ == self.distance_2 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control2()
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                    # 记录第三个装车点料高和时间
                    if self.work_finish:
                        self.load_height3 = self.load_height.data
                        self.load_time3 = datetime.datetime.now()

            elif self.icps_differ_num == '0012': # 装料两次的控制程序
                if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control0()
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                    # 记录第一个装车点料高和时间
                    if self.icps_differ == self.distance_2:
                        self.load_height1 = self.load_height.data
                        self.load_time1 = datetime.datetime.now()
                if self.icps_differ == self.distance_2 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control2()
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                    # 记录第二个装车点料高和时间
                    if self.work_finish:
                        self.load_height2 = self.load_height.data
                        self.load_time2 = datetime.datetime.now()

            elif self.icps_differ_num == '0112': # 装料两次的控制程序
                if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control0()
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                    # 记录第一个装车点料高和时间
                    if self.icps_differ == self.distance_1:
                        self.logging.debug("记录装车时间1")
                        self.load_height1 = self.load_height.data
                        self.load_time1 = datetime.datetime.now()
                elif self.icps_differ == self.distance_1 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control2()
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                    # 记录第二个装车点料高和时间
                    if self.work_finish:
                        self.logging.debug("记录装车时间2")
                        self.load_height2 = self.load_height.data
                        self.load_time2 = datetime.datetime.now()

            elif self.icps_differ_num == '0001': # 装料一次的控制程序
                if self.icps_differ == self.distance_0 : # 判断车辆引导位置，执行相应装料点控制程序
                    self.load_control0()
                    self.height_load = self.load_height.data
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)
                if self.allow_plc_work == 0:
                    self.work_finish = 1
                    self.load_end_time = datetime.datetime.now()
                    self.time_record_flag = True
                    # 记录第一个装车点料高和时间
                    self.load_height1 = self.load_height.data
                    self.load_time1 = datetime.datetime.now()
                    coontrol_status_socket(self.allow_plc_work)
                    loader_status_socket(self.work_finish)

            if self.work_finish:
                # 更新数据库
                update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "truck_weight_out": self.truck_weight_out,
                        "load_level_height1": self.load_height1,
                        "load_level_height2": self.load_height2,
                        "load_level_height3": self.load_height3,
                        "load_time1": self.load_time1,
                        "load_time2": self.load_time2,
                        "load_time3": self.load_time3,
                        "loadestimate": self.loadestimate,
                    }
                )

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


    # def smooth(self):
    #     # 再做一次滤波（四个数据）
    #     is_smooth = False
    #     a = 0
    #     current_time = datetime.datetime.now()
    #     latest_data = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).limit(30).all()
    #     if len(latest_data) < 30:
    #         self.logging.debug('smooth: 数据不足30条!!')
    #         return True
    #     for i in range(len(latest_data) - 1):
    #         data_differ = latest_data[i+1].data - latest_data[i].data
    #         if abs(data_differ) < 1:
    #             a += 1
    #     if a == 29:
    #         self.logging.debug('smooth: 30s前到此刻数据平滑上升')
    #         is_smooth = True
    #     else:
    #         self.logging.debug('smooth: 数据存在波动,无法使用')
    #     return is_smooth


    def load_control0(self):

        self.logging.debug('control0')
        self.logging.debug(f'control0 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_0 :
            duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')
            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,duration.total_seconds()) # 估算当前装料量

            if duration.total_seconds() < 1*60:  # 前一分钟持续装料
                current_time = datetime.datetime.now()
                self.load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
                self.logging.debug(f'load_height:{self.load_height.data}')
                self.allow_plc_work = 1
                self.flag_load = 1
                self.work_weight_status = 1
                self.work_finish = 0
            else:
                # is_smooth = self.smooth() # 判断数据是否平稳
                # self.logging.debug(f'is_smooth: {is_smooth}')
                current_time = datetime.datetime.now()
                self.load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
                self.logging.debug(self.load_height.data)
                # if is_smooth == False: # 如果数据不平稳则停止前装料点装料
                #     self.allow_plc_work = 0
                #     self.flag_load = 2
                #     self.work_weight_status = 2
                #     self.work_finish = 0
                #     self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2 # 进入下一个装料点
                
                # else: # 数据平稳继续装料
                # load_duration = datetime.datetime.now() - self.load_start_time # 记录装料时间
                #current_time = datetime.datetime.now()
                #self.load_height = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).first()
                if self.sensor_status_ok(load_height=self.load_height) is not True: # 物位计异常，无数据，程序停止
                    return
                if self.load_height.data < self.load_level_limit1 : # 如果料高未超过限制，继续装料
                    self.allow_plc_work = 1
                    self.flag_load = 1
                    self.work_weight_status = 1
                    self.work_finish = 0
                else:  # 如果料高超过限制，停止装料
                    self.allow_plc_work = 0
                    self.flag_load = 0
                    self.work_weight_status = 2
                    self.work_finish = 0
                    self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2
                
                # # 如果当前料高未超过限制，且装料时间小于7分钟，继续装料
                # elif self.load_height.data < self.load_level_limit1:
                #     load_duration = datetime.datetime.now() - self.load_start_time # 记录装料时间
                #     current_time = datetime.datetime.now()
                #     self.load_height = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).first()
                #     # FIXME:打印最近的料高
                #     # self.logging.debug(self.load_height)
                #     if self.sensor_status_ok(load_height=self.load_height) is not True: # 物位计异常，无数据，程序停止
                #         return

                #     if load_duration.total_seconds() < 7*60 :
                #         self.allow_plc_work = 1
                #         self.flag_load = 1
                #         self.work_weight_status = 1
                #         self.work_finish = 0
                #     else:  # 如果料高超过限制或装料时间超过7分钟，停止装料
                #         self.allow_plc_work = 0
                #         self.flag_load = 0
                #         self.work_weight_status = 1
                #         self.work_finish = 0
                #         self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2
                # else:
                #     self.allow_plc_work = 0
                #     self.flag_load = 0
                #     self.work_weight_status = 1
                #     self.work_finish = 0
                #     self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2



    # 中装车点装料控制程序
    def load_control1(self):

        self.logging.debug('control1')
        self.logging.debug(f'control1 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_1 :

            duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')
            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,duration.total_seconds()) # 估算当前装料量
            current_time = datetime.datetime.now()
            self.load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
            # self.logging.debug(self.load_height)
            
            if self.sensor_status_ok(load_height=self.load_height) is not True: # 物位计异常，无数据，程序停止
                return


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

    # 后装车点装料控制程序
    def load_control2(self):

        self.logging.debug('control2')
        self.logging.debug(f'control2 -> icps_differ: {self.icps_differ}')

        if self.icps_differ == self.distance_2 or self.icps_differ == self.distance_1:
            duration = datetime.datetime.now() - self.load_start_time  # 计算装料持续时间
            self.logging.debug(f'duration:{duration}, duration.total_seconds(): {duration.total_seconds()}')
            self.loadestimate = self.weight_estimate(self.goods_type,self.loader_id,duration.total_seconds()) # 估算当前装料量
            current_time = datetime.datetime.now()
            self.load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
            # self.logging.debug(self.load_height)
            
            if self.sensor_status_ok(load_height=self.load_height) is not True: # 物位计异常，无数据，程序停止
                return


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
                self.load_end_time = datetime.datetime.now()
                self.time_record_flag = True

    def sensor_status_ok(self, load_height)-> bool:
        if load_height is None:
            self.allow_plc_work = 0
            self.work_finish = 0
            return False
        else:
            return True
        

    # 预估重量
    def weight_estimate(self, goods_type,loader_id,time_difference): 
        current_load_weight = 0.0
        per_second_weight = 0
        #筛选数据, 注意需要去除当前正在装车的数据
        filtered_traffic = Traffic.query.filter(and_(Traffic.loaderid==loader_id,Traffic.goodstype==goods_type)).all()[:-1]

        filtered_data_length = len(filtered_traffic)
        #self.logging.debug(f'filtered_data_length{filtered_data_length}')
        # 没有数据直接退出
        if filtered_data_length == 0:
            return None

        #提取筛选后数据的某一属性
        start_load_times = [traffic.loadstarttime for traffic in filtered_traffic if traffic.loadstarttime is not None]
        stop_load_times = [traffic.loadtime2 for traffic in filtered_traffic if traffic.loadtime2 is not None]

        loader_task = [traffic.loadcurrent for traffic in filtered_traffic]

        #计算装载时间
        load_time = [(stop - start).total_seconds() for start, stop in zip(start_load_times, stop_load_times)]

        for i in range(filtered_data_length):
            try:
                per_second_weight += loader_task[i] / load_time[i] * 1.0
            except ZeroDivisionError:
                print('error')
                return None

        per_second_weight /= filtered_data_length
        current_load_weight = per_second_weight * time_difference

        return current_load_weight


# 将每个装料点定义成一个类的实例
load_point_dict = dict()

def create_loader_points():
    global load_point_dict
    logging.debug(LoadPoint.loader_id_list)
    load_point_list = [LoadPoint(i) for i in LoadPoint.loader_id_list]
    logging.debug(load_point_list)

    # 生成字典
    load_point_dict = dict(zip(LoadPoint.loader_id_list, load_point_list))
    logging.debug(load_point_dict)

if len(load_point_dict) == 0:
    logging.debug("=======================")
    create_loader_points()
