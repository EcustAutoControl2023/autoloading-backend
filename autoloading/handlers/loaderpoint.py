import datetime
import logging
from operator import and_
import socket

from sqlalchemy import false
from sqlalchemy.engine import ObjectKind
from autoloading.config import TRUCK_CONFIRM
from flask import jsonify, session
from autoloading.handlers.truck_store import insert_truck_content, update_truck_content
from autoloading.models import sensor
from autoloading.models.sensor import Traffic, loader_num
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
        self.truck_id   = ''
        self.truck_load = 0
        self.data_type  = -1
        self.store_id   = 0
        self.loader_id  = 0
        self.box_length = 0
        self.box_width  = 0
        self.box_height = 0
        self.distance_0 = 0
        self.distance_1 = 0
        self.distance_2 = 0
        self.load_current = 0
        self.icps_differ_num = None
        self.icps_differ = ''
        self.load_start_time = datetime.datetime.now()
        self.load_end_time = datetime.datetime.now()
        self.allow_plc_work = 0
        self.allow_work_flag = None
        self.flag_load = 0
        self.work_weight_status = 0
        self.work_weight_reality = None
        self.work_finish = 1
        self.time_record_flag = True
        self.height_load = None

        # XXX: 定义装料高度上限
        self.load_level_limit1 = 0
        self.load_level_limit2 = 0
        self.load_level_limit3 = 0
        self.load_height = 0

        self.load_height1 = None
        self.load_height2 = None
        self.load_height3 = None

        self.load_time1 = None
        self.load_time2 = None
        self.load_time3 = None

        self.loadestimate = None

        self.five_seconds_ago = datetime.timedelta(seconds=5)

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

        if self.data_type == 0:

            # TODO: 接收到客户端请求，计算并发送装车策略
            if (self.distance_0 != self.distance_1) and (self.distance_0 != self.distance_2) and (self.distance_1 != self.distance_2):
                self.work_total = 3
                self.icps_differ_num = '0123' # 共装车三次，三个装车点各不相同
                self.icps_differ = self.distance_0
            elif (self.distance_0 == self.distance_1) and (self.distance_1 != self.distance_2) :
                self.work_total = 2
                self.icps_differ_num = '0012' # 共装车两次，前装车点和中装车点相同
                self.icps_differ = self.distance_0
            elif (self.distance_1 == self.distance_2) and (self.distance_1 != self.distance_0) :
                self.work_total = 2
                self.icps_differ_num = '0112' # 共装车两次，中装车点和后装车点相同
                self.icps_differ = self.distance_0
            elif (self.distance_0 == self.distance_1) and (self.distance_1== self.distance_2) :
                self.work_total = 1
                self.icps_differ_num = '0001' # 共装车一次，三个装车点相同
                self.icps_differ = self.distance_0
            else:
                self.work_total = 0
                self.icps_differ_num = None # 无装车策略
                self.work_finish = 1
                self.load_end_time = datetime.datetime.now()
                self.time_record_flag = True

            logging.debug(f'icps_differ: {self.icps_differ_num}')

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
            self.work_finish = 0 if (self.icps_differ_num is None) and (self.work_finish == 1) else self.work_finish

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
            # load_level = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
            # load_level_data = None
            # if load_level is None:
            #     # FIXME: 第一个数据读取不到
            #     load_level_data = 4040
            # else:
            #     load_level_data = load_level.data
            # logging.debug(load_level_data)

            # XXX:基准问题（箱体+轮子
            # 4440: 物位计的高度
            # 1300：轮子高度
            # self.load_level_limit = 4040 # 4440 - 1300 - box_height*1000 + 60
            # XXX:从数据库中查料高(三堆0，1，2)
            load_level_height0 = 800
            # XXX:确认limit和height0的大小关系
            # XXX:确认装的是第几堆（根据装料点判断

            logging.debug(f'icps_differ: {self.icps_differ}')
            if self.icps_differ_num == '0123': # 装料三次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                    # 记录第一个装车点料高和时间
                    if self.icps_differ == self.distance_1:
                        self.load_height1 = self.load_height
                        self.load_time1 = datetime.datetime.now()
                elif self.icps_differ == self.distance_1 :
                    self.load_control1()
                    # 记录第二个装车点料高和时间
                    if self.icps_differ == self.distance_2:
                        self.load_height2 = self.load_height
                        self.load_time2 = datetime.datetime.now()
                elif self.icps_differ == self.distance_2 :
                    self.load_control2()
                    # 记录第三个装车点料高和时间
                    if self.work_finish:
                        self.load_height3 = self.load_height
                        self.load_time3 = datetime.datetime.now()

            elif self.icps_differ_num == '0012': # 装料两次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                    # 记录第一个装车点料高和时间
                    if self.icps_differ == self.distance_2:
                        self.load_height1 = self.load_height
                        self.load_time1 = datetime.datetime.now()
                if self.icps_differ == self.distance_2 :
                    self.load_control2()
                    # 记录第二个装车点料高和时间
                    if self.work_finish:
                        self.load_height2 = self.load_height
                        self.load_time2 = datetime.datetime.now()

            elif self.icps_differ_num == '0112': # 装料两次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                    # 记录第一个装车点料高和时间
                    if self.icps_differ == self.distance_1:
                        self.load_height1 = self.load_height
                        self.load_time1 = datetime.datetime.now()
                elif self.icps_differ == self.distance_1 :
                    self.load_control2()
                    # 记录第二个装车点料高和时间
                    if self.work_finish:
                        self.load_height2 = self.load_height
                        self.load_time2 = datetime.datetime.now()

            elif self.icps_differ_num == '0001': # 装料一次的控制程序
                if self.icps_differ == self.distance_0 :
                    self.load_control0()
                if self.allow_plc_work == 0:
                    self.work_finish = 1
                    self.load_end_time = datetime.datetime.now()
                    self.time_record_flag = True
                    # 记录第一个装车点料高和时间
                    self.load_height1 = self.load_height
                    self.load_time1 = datetime.datetime.now()

            # 更新数据库
            update_truck_content(
                truckid=self.truck_id,
                loaderid=self.loader_id,
                update_data={
                    "load_start_time": self.load_start_time,
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


    def smooth(self):
        # 再做一次滤波（四个数据）
        is_smooth = False
        a = 0
        current_time = datetime.datetime.now()
        latest_data = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).limit(30).all()
        if len(latest_data) < 30:
            logging.debug('smooth: 数据不足30条!!')
            return True
        for i in range(len(latest_data) - 1):
            data_differ = latest_data[i+1].data - latest_data[i].data
            if abs(data_differ) < 1:
                a += 1
        if a == 29:
            logging.debug('smooth: 30s前到此刻数据平滑上升')
            is_smooth = True
        else:
            logging.debug('smooth: 数据存在波动,无法使用')
        return is_smooth

    # 预估重量
    def weight_estimate(self, time_difference):

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

                current_time = datetime.datetime.now()
                self.load_height = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).first()
                # FIXME:打印最近的料高
                # logging.debug(self.load_height)
                if self.sensor_status_ok(load_height=self.load_height) is not True:
                    return
                self.load_height1 = self.load_height.data


                logging.debug(self.load_height.data)
                if is_smooth == False:
                    self.allow_plc_work = 0
                    self.flag_load = 0
                    self.work_weight_status = 1
                    self.work_finish = 0
                    self.icps_differ = self.distance_1 if self.distance_0 != self.distance_1 else self.distance_2
                # 如果当前料高未超过限制，且装料时间小于7分钟，继续装料
                elif float(int(self.load_height.data)) < self.load_level_limit1:
                    load_duration = datetime.datetime.now() - self.load_start_time
                    current_time = datetime.datetime.now()
                    self.load_height = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).first()
                    # FIXME:打印最近的料高
                    # logging.debug(self.load_height)
                    if self.sensor_status_ok(load_height=self.load_height) is not True:
                        return

                    self.load_height1 = self.load_height.data
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
            current_time = datetime.datetime.now()
            self.load_height = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).first()
            # FIXME:打印最近的料高
            # logging.debug(self.load_height)
            if self.sensor_status_ok(load_height=self.load_height) is not True:
                return

            self.load_height2 = self.load_height.data
            if self.load_height.data < self.load_level_limit2:
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
            current_time = datetime.datetime.now()
            self.load_height = self.Sensor.query.filter(self.Sensor.time >= current_time - self.five_seconds_ago).order_by(self.Sensor.id.desc()).first()
            # FIXME:打印最近的料高
            # logging.debug(self.load_height)
            if self.sensor_status_ok(load_height=self.load_height) is not True:
                return

            self.load_height3 = self.load_height.data
            if self.load_height.data < self.load_level_limit3:
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
