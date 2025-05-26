import datetime
import logging
from datetime import timedelta
from queue import Queue
import socket
from flask import json, jsonify, session
from sqlalchemy import False_
from autoloading.handlers.truck_store import insert_truck_content, update_truck_content
from autoloading.models.sensor import Traffic, loader_num
from autoloading.config import create_logger

for i in range(loader_num):
    exec(f"from autoloading.models.sensor import Sensor{i + 1}")


# 生成返回值
def gen_return_data(
    time,
    store_id: int = 1,
    loader_id: str = "401A",
    operating_stations={},
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
    """
    物位计数据类
    """

    def __init__(self, data: float):
        self.data = data


class LoadPoint:
    load_level_height_list: list[float] = []  # 装料高度列表
    # 定义装料点的id列表 [1-20]
    loader_id_list = [
        "401A",
        "402A",
        "403A",
        "401B",
        "402B",
        "403B",
        "501A",
        "502A",
        "503A",
        "501B",
        "502B",
        "503B",
        "601A",
        "602A",
        "603A",
        "604A",
        "601B",
        "602B",
        "603B",
        "604B",
    ]
    # 定义装料点的index列表
    loader_index_list = [i for i in range(loader_num)]
    loader_index_dict = dict(zip(loader_id_list, loader_index_list))
    # logging.debug(f'loader_index_dict: {loader_index_dict}')
    # 定义类变量SensorList, 用于存储每个Sensor类
    SensorList = list()
    for i in range(loader_num):
        exec(f"SensorList.append(Sensor{i + 1})")
    ServerList = [
        ("172.16.175.59", 8234),
        ("172.16.175.65", 8234),
        ("172.16.175.71", 8234),
        ("172.16.175.77", 8234),
        ("172.16.175.83", 8234),
        ("172.16.175.89", 8234),
        ("172.16.175.95", 8234),
        ("172.16.175.101", 8234),
        ("172.16.175.107", 8234),
        ("172.16.175.113", 8234),
        ("172.16.175.119", 8234),
        ("172.16.175.125", 8234),
        ("172.16.175.131", 8234),
        ("172.16.175.137", 8234),
        ("172.16.175.143", 8234),
        ("172.16.175.149", 8234),
        ("172.16.175.155", 8234),
        ("172.16.175.161", 8234),
        ("172.16.175.167", 8234),
        ("172.16.175.173", 8234),
    ]  # 物位计的ip地址、端口号
    LocationList = [
        212,
        212,
        212,
        212,
        212,
        212,
        212,
        212,
        212,
        212,
        212,
        212,
        213,
        213,
        213,
        213,
        213,
        213,
        213,
        213,
    ]
    StackposList = [
        "401A",
        "402A",
        "403A",
        "401B",
        "402B",
        "403B",
        "501A",
        "502A",
        "503A",
        "501B",
        "502B",
        "503B",
        "601A",
        "602A",
        "603A",
        "604A",
        "601B",
        "602B",
        "603B",
        "604B",
    ]
    # LoadCoefficient = {
    #     "黄豆": {
    #         "侧开": [(9, 10), 9, 8],
    #         "全开": [(9.5, 10.5), 10, 9],
    #         "半开": [(9.5, 10.5), 10, 9]
    #     },
    #     "油菜籽": {
    #         "侧开": [(9, 9.8), 9.8, 9],
    #         "全开": [(9.7, 10.7), 9.7, 9.2],
    #         "半开": [(9.7, 10.7), 9.7, 9.2]
    #     }
    # }

    # LoadCoefficient = {
    #     "黄豆": {
    #         "侧开": [(0.37, 0.1646, 6.8624, 0.5091), 9, 8],
    #         "全开": [(-0.7263, 5.3778, 1.1984, 0.2529), 10, 9],
    #         "半开": [(-0.7263, 5.3778, 1.1984, 0.2529), 10, 9]
    #     },
    #     "油菜籽": {
    #         "侧开": [(-0.6926, 5.239, 1.5352, 0.2067), 9.8, 9],
    #         "全开": [(-0.6926, 5.239, 1.5352, 0.2067), 9.7, 9.2],
    #         "半开": [(-0.6926, 5.239, 1.5352, 0.2067), 9.7, 9.2]
    #     }
    # }

    LoadCoefficient = {
        "黄豆": {
            "侧开": [
                (0.37, 0.1646, 6.8624, 0.5091),
                (0.37, 0.1646, 6.8624, 0.5091),
                (0.37, 0.1646, 6.8624, 0.5091),
            ],
            "全开": [
                (-0.7263, 5.3778, 1.1984, 0.2529),
                (-0.7263, 5.3778, 1.1984, 0.2529),
                (-0.7263, 5.3778, 1.1984, 0.2529),
            ],
            "半开": [
                (-0.7263, 5.3778, 1.1984, 0.2529),
                (-0.7263, 5.3778, 1.1984, 0.2529),
                (-0.7263, 5.3778, 1.1984, 0.2529),
            ],
        },
        "油菜籽": {
            "侧开": [
                (-0.6926, 5.239, 1.5352, 0.2067),
                (-0.6926, 5.239, 1.5352, 0.2067),
                (-0.6926, 5.239, 1.5352, 0.2067),
            ],
            "全开": [
                (-0.6926, 5.239, 1.5352, 0.2067),
                (-0.6926, 5.239, 1.5352, 0.2067),
                (-0.6926, 5.239, 1.5352, 0.2067),
            ],
            "半开": [
                (-0.6926, 5.239, 1.5352, 0.2067),
                (-0.6926, 5.239, 1.5352, 0.2067),
                (-0.6926, 5.239, 1.5352, 0.2067),
            ],
        },
    }

    GoodsCoefficient = {
        "黄豆": {"巴西": 0.90, "美国": 1},
        "油菜籽": {"巴西": 0.94, "美国": 0.94},
    }

    def __init__(self, loader_id: str):
        self.Sensor = LoadPoint.SensorList[LoadPoint.loader_index_dict[loader_id]]
        self.server_ip = LoadPoint.ServerList[LoadPoint.loader_index_dict[loader_id]]
        self.hex_data = "01040A1100022216"  # 发送给物位计的命令
        self.byte_data = bytes.fromhex(self.hex_data)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.s.setblocking(False)

        self.req_time = None  # 任务开始时间
        self.task_finish_time = None  # 任务完成时间

        self.truck_id = ""  # 车牌信息
        self.truck_load = 0  # 车辆最大载重
        self.data_type = -1  # 数据类型，0：请求作业策略；1：请求允许作业；2：出闸重量；3：请求实时作业情况数据；4：识别有误弹窗确认
        self.store_id = 0  # 装料仓库编号
        self.loader_id = loader_id  # 装料机编号
        self.box_length = 0  # 箱体长
        self.box_width = 0  # 箱体宽
        self.box_height = 0  # 箱体高

        # FIXME: 弃用
        self.distance_0 = None  # 车辆前装车点距离
        self.distance_1 = None  # 车辆中装车点距离
        self.distance_2 = None  # 车辆后装车点距离
        # INFO: 改用
        self.distance_list = []  # 车辆装车点距离列表
        self.icps_differ_index = 0  # 装车点索引
        self.load_policy = []  # 装车策略 value("height" or "time") 缩写("h" or "t")

        self.icps_differ_num = None  # 车辆作业策略
        self.icps_differ = ""  # 车辆引导目标位置
        self.icps_differ_new = []  # 返回的引导位置
        self.icps_flag = 0  # 判断装料情况
        self.load_start_time = datetime.datetime.now()  # 车辆开始装料时间
        self.load_end_time = None  # 车辆结束装料时间
        self.allow_plc_work = 0  # PLC启停控制；0：停止，1：启动
        self.allow_work_flag = None  #
        self.flag_load = 0  # 装料机状态；0：未装车，1：装车中，2：故障
        self.work_weight_status = (
            0  # 作业执行情况；0：未开始，1：正在执行，2：已完成，3：检测溢出，被动完成
        )
        # self.work_weight_reality = None  # 作业装料情况(当前装料量)
        self.work_finish = 0  # 任务是否完成，0：未完成，1：完成
        self.time_record_flag = True  # 时间记录标志
        self.insert_traffic_flag = False  # 判断是否是新任务
        self.height_load = None  # 需要返回给请求方的实时料高
        self.goods_type = ""  # 货物类型
        self.goods_source = "巴西"  # 货物来源
        self.work_total = 0  # 当前任务装料总次数
        self.load_current = 0  # 本次装载量(任务装载量)
        self.loading_state = None  # 下料状态，true：下料中，false停止下料
        self.type_of_opening = ""  # 开口类型
        self.opening_length_bias = 0  # 侧边距
        self.opening_width_bias = 0  # 尾边距
        self.opening_length = 0  # 开口长
        self.opening_width = 0  # 开口宽

        # XXX: 定义装料高度上限
        # FIXME: 弃用
        self.load_level_limit1 = 3.7  # 3.72      # 第一次装料高度限制
        self.load_level_limit2 = 3.7  # 3.65       # 第二次装料高度限制
        self.load_level_limit3 = 3.7  # 3.65       # 第三次装料高度限制
        # INFO: 改用
        self.load_level_limit_list = []  # 装料高度限制列表

        self.load_height = SensorData(-1)  # 实时装料高度
        # FIXME: 弃用
        self.load_height1_begin = 0  # 新增，第1堆初始高度
        self.load_height2_begin = 0  # 新增，第2堆初始高度
        self.load_height3_begin = 0  # 新增，第3堆初始高度
        self.load_weight1_end = 0  # 新增，第1堆结束重量
        self.load_weight2_end = 0  # 新增，第2堆结束重量
        # INFO: 改用
        self.load_height_begin_list = []  # 每堆初始高度列表
        self.load_weight_end_list = []  # 每堆结束重量列表
        self.load_height_queue = Queue(maxsize=20)  # 新增，最近10条高度（队列）
        self.load_height_list = list()  # 新增，最近10条高度（list）

        # FIXME: 弃用
        self.load_level_height1 = None  # 第一次装料时高度
        self.load_level_height2 = None  # 第二次装料时高度
        self.load_level_height3 = None  # 第三次装料时高度
        # INFO: 改用
        self.load_level_height_list = []  # 每次装料高度列表

        # FIXME: 弃用
        self.load_time1 = None  # 第一次装料完成时间
        self.load_time2 = None  # 第二次装料完成时间
        self.load_time3 = None  # 第三次装料完成时间
        # INFO: 改用
        self.load_time_list = []  # 装料完成时间列表

        self.load_time = datetime.timedelta(0)  # 装料所用时间
        # FIXME: 弃用
        self.load_start_time1_flag = True  # 中装料点时间记录控制标志
        self.load_start_time2_flag = True  # 后装料点时间记录控制标志
        # INFO: 改用
        self.load_start_time_flag_list = []  # 装料点时间记录控制标志列表
        self.load_start_time_list = []  # 各个装料点开始时间列表
        # FIXME: 弃用
        self.load_stop_time1 = datetime.timedelta(0)  # 第一堆料停料时间段
        self.load_stop_time2 = datetime.timedelta(0)  # 第二堆料停料时间段
        self.load_stop_time3 = datetime.timedelta(0)  # 第三堆料停料时间段
        # INFO: 改用
        self.load_stop_time_list = []  # 装料点停料时间段列表

        self.loadestimate = 0  # 装料预估重量
        self.truck_weight_out = 0  # 合作方给出场重量

        self.duration = float(0)  # 装料持续时间

        # self.five_seconds_ago = datetime.timedelta(seconds=5)      # 物位计滞后时差
        self.logging = create_logger(f"装料点-{loader_id}")  # 装料点日志

        self.jobid = 0  # 任务ID编号
        self.loadstatus = "未装车"
        self.location = LoadPoint.LocationList[LoadPoint.loader_index_dict[loader_id]]
        self.stackpos = LoadPoint.StackposList[LoadPoint.loader_index_dict[loader_id]]

        self._weight_in = 0  # 车辆入场重量
        self.temp_manual_stop = 0  # 临时手动停止标志
        self.breakdowncode = 0  # 故障代码
        self.emergency_stop = 0  # 紧急停止标志
        self.auto_select = 0  # 自动选择标志
        self.belt_motor_run = 0  # 皮带电机运行标志

        self.speed = 0.35  # 下料速率
        self.guide_position = []  # 装车点位 List

    # TODO: 函数输入参数改为字典
    def load_control(
        self,
        req_time,
        data_type,
        truck_id,
        truck_load,
        box_length,
        box_width,
        box_height,
        truck_weight_in,
        truck_weight_out,
        goods_type,
        store_id,
        loader_id,
        load_current,
        temp_manual_stop,
        distance0,
        distance1,
        distance2,
        icps_differ_current,
        picture_url_plate,
        picture_url_request,
        jobid,
        loading_state,
        type_of_opening,
        opening_length_bias,
        opening_width_bias,
        opening_length,
        opening_width,
        breakdowncode,
        emergency_stop,
        auto_select,
        belt_motor_run,
        guide_position,
    ):
        self.req_time = datetime.datetime.now()
        self.data_type = data_type
        self.truck_id = truck_id
        self.truck_load = truck_load
        self.store_id = store_id
        self.loader_id = loader_id
        self.box_length = box_length
        self.box_width = box_width
        self.box_height = box_height
        # FIXME: 弃用
        self.distance_0 = distance0
        self.distance_1 = distance1
        self.distance_2 = distance2

        self.load_current = load_current - 0.2  # 保守装，少2吨，临时调整
        self.goods_type = goods_type
        self.truck_weight_out = truck_weight_out
        self.jobid = jobid
        self._weight_in = truck_weight_in
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
        self.guide_position = guide_position

        if self.data_type == 0:  # 接收任务信息并发送引导策略
            self.logging.debug("data_type:0")
            self.logging.debug(f"truck_id:{self.truck_id}开始任务")
            self.logging.debug(
                f"引导点位列表: {self.guide_position}, 引导点位个数: {len(self.guide_position)}"
            )

            traffic = (
                Traffic.query.filter_by(loaderid=self.loader_id)
                .order_by(Traffic.id.desc())
                .first()
            )
            self.logging.debug(f"traffic: {traffic}")
            # 判断是否有新车辆到达, 如果有新车辆到达，初始化装料点状态
            if traffic is None or (traffic.truckid != self.truck_id):
                self.logging.debug(f"新装料任务：{self.truck_id}")
                # 根据上一车的装车数据调整本车的装车系数
                # self.load_co = self.get_adjustment_co(self.LoadCoefficient)
                # self.goods_co = self.get_adjustment_co(self.GoodsCoefficient)
                self.work_finish = 0
                self.icps_flag = 0
                self.insert_traffic_flag = True
                self.time_record_flag = True
                self.loadstatus = "装车中" if self.work_finish == 0 else "装车完成"

                # FIXME: 弃用
                self.load_start_time1_flag = True
                self.load_start_time2_flag = True
                # INFO: 改用 load_start_time_flag_list, 长度通过装车点位个数决定
                self.load_start_time_flag_list = [
                    True for i in range(len(self.guide_position))
                ]
                self.load_start_time_list = [
                    datetime.datetime.now() for i in range(len(self.guide_position))
                ]

                # FIXME: 弃用
                self.icps_differ = self.distance_0
                # INFO: 改用 icps_differ_index, 通过索引获取当前装车点位
                self.icps_differ_index = 0

                # FIXME: 弃用
                self.load_height1_begin = 0
                self.load_height2_begin = 0
                self.load_height3_begin = 0
                # INFO: 改用 load_height_begin_list, 长度通过装车点位个数决定
                self.load_height_begin_list = [
                    0.0 for i in range(len(self.guide_position))
                ]

                # FIXME: 弃用
                self.load_weight1_end = 0
                self.load_weight2_end = 0
                # INFO: 改用 load_weight_end_list, 长度通过装车点位个数决定
                self.load_weight_end_list = [
                    0.0 for i in range(len(self.guide_position))
                ]

                self.load_height_queue = Queue(maxsize=20)
                self.load_height_list = list()
                self.load_height = SensorData(-1)

                # FIXME: 弃用
                self.load_level_limit1 = (
                    0.83 + self.box_height
                )  # 第一次装料高度限制，1.2为车厢底
                self.load_level_limit2 = 0.83 + self.box_height  # 第二次装料高度限制
                self.load_level_limit3 = 0.83 + self.box_height  # 第三次装料高度限制
                # INFO: 装料高度限制改用 load_level_limit_list, 长度通过装车点位个数决定
                self.load_level_limit_list = [
                    0.83 + self.box_height for i in range(len(self.guide_position))
                ]

                # FIXME: 弃用
                self.load_stop_time1 = datetime.timedelta(0)  # 初始化停料时间
                self.load_stop_time2 = datetime.timedelta(0)  # 初始化停料时间
                self.load_stop_time3 = datetime.timedelta(0)  # 初始化停料时间
                # INFO: 初始化停料时间改用 load_stop_time_list, 长度通过装车点位个数决定
                self.load_stop_time_list = [
                    datetime.timedelta(0) for i in range(len(self.guide_position))
                ]

                # INFO: 初始化装料时间列表 load_time_list, 长度通过装车点位个数决定
                self.load_time_list = [
                    datetime.datetime.now() for i in range(len(self.guide_position))
                ]

                # INFO: 初始化装料高度列表 load_level_height_list, 长度通过装车点位个数决定
                self.load_level_height_list = [
                    0.0 for i in range(len(self.guide_position))
                ]

                self.load_policy = []  # 装车策略

            # self.logging.debug(f"distance_0:{self.distance_0}")
            # self.logging.debug(f"distance_1:{self.distance_1}")
            # self.logging.debug(f"distance_2:{self.distance_2}")
            # self.logging.debug(f"icps_differ:{self.icps_differ}")

            self.logging.debug(f"icps_differ_index: {self.icps_differ_index}")
            self.logging.debug(
                f"icps_differ: {self.guide_position[self.icps_differ_index]}"
            )

            if self.guide_position is not None and len(self.guide_position) > 0:
                self.work_total = len(self.guide_position)  # 装车点位个数
                self.icps_differ_new = self.guide_position[self.icps_differ_index :]
                # 装车策略["h", "t", "t", ...., "t"]
                self.load_policy = [
                    "h" if i < 1 else "t" for i in range(len(self.guide_position))
                ]

            else:
                self.logging.debug("引导点位列表为空")
                self.work_total = 0
                self.work_finish = 1
                self.load_end_time = datetime.datetime.now()
                self.time_record_flag = True
                self.insert_traffic_flag = True
                self.icps_differ_new = []
                self.load_policy = []

            # 打印装车策略
            self.logging.debug(
                f"装车点位个数: {self.work_total}, 装车策略: {self.load_policy}"
            )

            # 将数据存入数据库中, 仅在每个装车任务开始时，插入一条新的记录
            self.logging.debug(f"self.insert_traffic_flag: {self.insert_traffic_flag}")
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
                    type_of_opening=self.type_of_opening,
                    opening_length_bias=self.opening_length_bias,
                    opening_width_bias=self.opening_width_bias,
                    opening_length=self.opening_length,
                    opening_width=self.opening_width,
                    load_time=0,
                )

            # 如果引导策略反馈的 icps_differ 为空，且 work_finish=1，标识任务完成
            # self.work_finish = 1 if (self.icps_differ_num is None) and (self.work_finish == 1) else self.work_finish
            result = gen_return_data(
                time=self.req_time,
                store_id=self.store_id,
                loader_id=self.loader_id,
                operating_stations={
                    "truck_id": self.truck_id,
                    "icps_differ": self.guide_position[
                        self.icps_differ_index + self.work_finish :
                    ],
                    "work_finish": self.work_finish,
                },
            )

        elif data_type == 1:  # 车辆引导到位，发送PLC控制策略
            self.logging.debug(f"{self.truck_id}请求data_type:1")
            self.logging.debug(f"temp_manual_stop: {self.temp_manual_stop}")
            self.logging.debug(f"loading_state: {self.loading_state}")
            self.logging.debug(f"icps_differ_current: {icps_differ_current}")

            if icps_differ_current != None:
                self.icps_differ_index = icps_differ_current
                self.logging.debug(
                    f"【调试变量】更正装料点位->icps_differ: {self.icps_differ_index}"
                )

            # self.logging.debug(f"loading_state:{self.loading_state}")
            # self.logging.debug(f"loading_state==false:{self.loading_state==0}")
            if self.loading_state == 0:
                self.allow_plc_work = 0
                result = gen_return_data(
                    time=self.req_time,
                    store_id=self.store_id,
                    loader_id=self.loader_id,
                    operating_stations={
                        "truck_id": self.truck_id,
                        "allow_plc_work": self.allow_plc_work,
                        "work_finish": self.work_finish,
                        "work_weight_status": self.work_weight_status,
                        "loading_state": self.loading_state,
                    },
                )

                return result

            # 记录开始装料时间
            if self.time_record_flag:
                self.load_start_time = datetime.datetime.now()
                self.logging.debug(f"load_start_time: {self.load_start_time}")
                self.duration = float(0)
                self.time_record_flag = False
                # 获取当前的物料种类调整系数
                from autoloading.handlers.config import get_config

                co_config = get_config(
                    loader_id=self.loader_id, goods_type=self.goods_type
                )
                self.speed = co_config["weight"] / co_config["duration"]
                logging.debug(f"下料速率: {self.speed}")
                update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "load_start_time": self.load_start_time,
                    },
                )

            # FIXME: 待修改
            if self.temp_manual_stop != 0:
                self.logging.debug("手动停止")
                self.logging.debug(f"料高列表: {self.load_height_list}")
                self.logging.debug(
                    f"在第{self.icps_differ_index + 1}个点位[{self.guide_position[self.icps_differ_index]}]手动停止"
                )

                return self.stop(self.truck_id, self.loader_id)

            self.logging.debug(f"当前策略: {self.print_current_policy()}")

            if self.work_finish == 0:
                if self.duration > 1800:
                    self.time_record_flag = True
                    self.insert_traffic_flag = True
                    return None
                previous_icps_differ_index = self.icps_differ_index
                self.load_control_final()
                if (
                    self.icps_differ_index != previous_icps_differ_index
                    or self.work_finish
                ):
                    self.logging.debug(
                        f"第{previous_icps_differ_index + 1}个装车点位装料完毕，记录装车数据"
                    )
                    # 记录装车点位装料完成时间
                    self.load_time_list[previous_icps_differ_index] = (
                        datetime.datetime.now()
                    )
                    # 记录装车点位装料完成时物位高度
                    self.load_level_height_list[previous_icps_differ_index] = (
                        self.load_height.data
                    )
                    # 记录装车点位装料完成时估计装车重量
                    self.load_weight_end_list[previous_icps_differ_index] = (
                        self.loadestimate
                    )
                    self.logging.debug(f"load_time_list: {self.load_time_list}")
                    self.logging.debug(
                        f"load_level_height_list: {self.load_level_height_list}"
                    )
                    self.logging.debug(
                        f"load_weight_end_list: {self.load_weight_end_list}"
                    )

                    # 更新数据库
                    update_truck_content(
                        truckid=self.truck_id,
                        loaderid=self.loader_id,
                        update_data={
                            "loadtimelist": json.dumps(
                                self.load_time_list,
                                default=str,
                            ),
                            "loadlevelheightlist": json.dumps(
                                self.load_level_height_list,
                                default=str,
                            ),
                            "loadweightendlist": json.dumps(
                                self.load_weight_end_list,
                                default=str,
                            ),
                        },
                    )

                self.loadstatus = "装车中" if self.work_finish == 0 else "装车完成"
                if self.work_finish:
                    self.logging.debug("任务完成，记录装车时间")
                    self.load_end_time = datetime.datetime.now()
                    # 更新数据库
                    update_truck_content(
                        truckid=self.truck_id,
                        loaderid=self.loader_id,
                        update_data={
                            "truck_weight_out": self.truck_weight_out,
                            "loadestimate": self.loadestimate,
                            "loadheight": self.load_height.data,
                            "loadstatus": self.loadstatus,
                            "goodstype": self.goods_type,
                            "loadendtime": self.load_end_time,
                            "loadtimetotal": self.load_time.total_seconds(),
                        },
                    )
                    self.load_end_time = None
                else:
                    update_truck_content(
                        truckid=self.truck_id,
                        loaderid=self.loader_id,
                        update_data={
                            "loadheight": self.load_height.data,
                            "loadstatus": self.loadstatus,
                        },
                    )

            from .socket import control_status_socket, loader_status_socket

            control_status_socket(
                {"value": self.allow_plc_work, "loaderid": self.loader_id}
            )
            loader_status_socket(
                {"value": self.work_finish, "loaderid": self.loader_id}
            )

            self.logging.debug(f"[type1]work_finish:{self.work_finish}")
            self.logging.debug(f"[type1]loadstatus:{self.loadstatus}")
            self.logging.debug(f"[type1]allow_plc_work:{self.allow_plc_work}")
            self.height_load = self.get_sensor_data().data
            result = gen_return_data(
                time=self.req_time,
                store_id=self.store_id,
                loader_id=self.loader_id,
                operating_stations={
                    "truck_id": self.truck_id,
                    "work_weight_status": self.work_weight_status,
                    "work_weight_reality": self.loadestimate,
                    "flag_load": self.flag_load,
                    "height_load": self.height_load,
                    "allow_plc_work": self.allow_plc_work,
                    "work_finish": self.work_finish,
                },
            )

        elif data_type == 2:
            self.logging.debug(f"{self.truck_id}请求data_type:2")
            update_truck_content(
                truckid=self.truck_id,
                loaderid=self.loader_id,
                update_data={
                    "truck_weight_out": self.truck_weight_out,
                },
            )
            result = gen_return_data(
                time=self.req_time,
                store_id=self.store_id,
                loader_id=self.loader_id,
                operating_stations={
                    "truck_id": self.truck_id,
                    "work_total": self.work_total,
                },
            )

        elif data_type == 4:
            from autoloading.config import TRUCK_CONFIRM

            self.logging.debug("data_type:4")
            truck_id_confirm = session.get("truck_id_popup_confirm", True)
            if not truck_id_confirm:
                # 弹出车牌勘误窗口
                from .socket import truck_id_popup

                truck_id_popup({"img_url": picture_url_request})

                session["truck_id_popup_confirm"] = TRUCK_CONFIRM.get()
                truck_id_confirm = session["truck_id_popup_confirm"]

            result = gen_return_data(
                time=self.req_time,
                store_id=self.store_id,
                loader_id=self.loader_id,
                operating_stations={
                    "truck_id": self.truck_id,
                    "allow_work_flag": self.allow_work_flag,
                },
            )

        else:
            result = {"message": "无请求参数 KEY/VALUE 类型"}

        return jsonify(result)

    def update_weightout(
        self,
        guide_position,
        truck_id,
        loader_id,
        req_time,
        store_id,
        truck_weight_out,
    ):
        self.logging.debug(f"{truck_id}data_type:2")
        self.logging.debug(f"truck_weight_out:{truck_weight_out}")
        work_total = len(guide_position)
        update_truck_content(
            truckid=truck_id,
            loaderid=loader_id,
            update_data={
                "truck_weight_out": truck_weight_out,
            },
        )
        return gen_return_data(
            time=req_time,
            store_id=store_id,
            loader_id=loader_id,
            operating_stations={
                "truck_id": truck_id,
                "work_total": work_total,
            },
        )

    # 装料高度控制
    def load_control_final(self):
        self.logging.debug(f"len(self.load_height_list): {len(self.load_height_list)}")
        self.logging.debug(
            f"len(set(self.load_height_list)): {len(set(self.load_height_list))}"
        )
        # 记录开始时间
        if self.load_start_time_flag_list[self.icps_differ_index]:
            self.load_start_time_list[self.icps_differ_index] = datetime.datetime.now()
            self.load_start_time_flag_list[self.icps_differ_index] = False

        self.duration = (
            self.load_time.total_seconds()
            + (
                datetime.datetime.now()
                - self.load_start_time_list[self.icps_differ_index]
            ).total_seconds()
        )  # 计算装料持续时间
        self.logging.debug(f"load_control_time -> duration:{self.duration}")

        self.load_height = self.get_sensor_data()
        self.logging.debug(f"load_height:{self.load_height.data}")

        # 第一堆开始前，需要调整本车的高度限制
        if (
            self.icps_differ_index == 0
            and int(self.load_height_begin_list[self.icps_differ_index]) == 0
        ):
            if len(self.load_height_list) == 10:
                self.load_height_begin_list[self.icps_differ_index] = (
                    self.load_height_list[0]
                )
                if (
                    1.5 < self.load_height_begin_list[self.icps_differ_index] < 2.5
                    and len(set(self.load_height_list)) == 1
                ):  # 最近十条数据相同，表示扫描到底部加强筋，强制赋值
                    self.load_height1_begin = 1.2
                elif self.load_height_begin_list[self.icps_differ_index] < 1.2:
                    self.load_height1_begin = 1.2
                elif (
                    self.load_height_begin_list[self.icps_differ_index] > 3.5
                ):  # 如果扫描到的是顶部的加强筋，不装料，不估计重量
                    self.load_height_begin_list[self.icps_differ_index] = 0
                    self.allow_plc_work = 0  # PLC停止
                    self.flag_load = 0  # 装料机未装车
                    self.work_weight_status = 2  # 作业已完成
                    self.work_finish = 0  # 任务未完成
                    self.load_time = datetime.datetime.now() - self.load_start_time
                    # FIXME: 逻辑问题，需要讨论一下
                    # self.icps_differ_index += 1
                    self.logging.debug("第一堆扫描到顶部加强筋，车移动到第二个点位")
                else:  # 正常记录
                    self.load_height_begin_list[self.icps_differ_index] = (
                        self.load_height_list[0]
                    )

                if 1.15 <= self.load_height_begin_list[self.icps_differ_index] <= 1.5:
                    # 修改每次装料高度限制，按照实际箱底算
                    for i in range(len(self.guide_position)):
                        self.load_level_limit_list[i] = (
                            self.load_height_begin_list[self.icps_differ_index]
                            - 0.3
                            + self.box_height
                        )
                        print(
                            f"load_level_limit_list[{i}]:{self.load_level_limit_list[i]}"
                        )

                # INFO: 存入self.load_height_begin_list序列化列表
                update_truck_content(
                    truckid=self.truck_id,
                    loaderid=self.loader_id,
                    update_data={
                        "loadheightbeginlist": json.dumps(self.load_height_begin_list)
                    },
                )
            # 后续只需记录高度
        elif self.load_height_begin_list[self.icps_differ_index] == 0:
            self.logging.debug("重置物位高度")
            self.load_height = self.get_sensor_data(reset=True)
            self.load_height_begin_list[self.icps_differ_index] = self.load_height.data
            load_heightn_begin = self.load_height_begin_list[self.icps_differ_index]
            if load_heightn_begin < 1.2:
                self.load_height_begin_list[self.icps_differ_index] = 1.2
            self.load_height_queue.put(load_heightn_begin)
            self.load_height_list = list(self.load_height_queue.queue)
            self.logging.debug(f"load_height_list:{self.load_height_list}")

            # INFO: 存入self.load_height_begin_list序列化列表
            update_truck_content(
                truckid=self.truck_id,
                loaderid=self.loader_id,
                update_data={
                    "loadheightbeginlist": json.dumps(self.load_height_begin_list)
                },
            )

        self.logging.debug(f"load_control_height -> index: {self.icps_differ_index}")
        self.logging.debug(
            f"load_control_height -> 点位: {self.guide_position[self.icps_differ_index]}"
        )

        # 估算当前装料量
        self.loadestimate = self.weight_estimate(
            self.goods_type,
            self.loader_id,
            self.type_of_opening,
            self.load_policy[self.icps_differ_index],
            float(self.load_height.data),
            (
                0
                if self.icps_differ_index - 1 < 0
                else self.load_weight_end_list[self.icps_differ_index - 1]
            ),  # 上一堆装车重量
            self.load_height_begin_list[self.icps_differ_index],  # 装车起始高度
        )
        self.logging.debug(f"loadestimate:{self.loadestimate}")

        if (
            self.load_height.data < self.load_level_limit_list[self.icps_differ_index]
            and self.loadestimate <= self.load_current
        ):  # 如果料高/重量未超过限制，继续装料
            self.allow_plc_work = 1
            self.flag_load = 1
            self.work_weight_status = 1
            self.work_finish = 0
        elif self.loadestimate > self.load_current:
            if self.icps_differ_index < len(self.guide_position) - 1:
                self.logging.debug("重量已达到，后续装料点不再装料")
                self.icps_differ_index = len(self.guide_position) - 1
            else:
                self.logging.debug("重量已达到，无后续装料点，任务结束")
            self.allow_plc_work = 0
            self.flag_load = 0
            self.work_weight_status = 2
            self.work_finish = 1
            self.load_time += (
                datetime.datetime.now()
                - self.load_start_time_list[self.icps_differ_index]
            )
            self.load_end_time = datetime.datetime.now()
        else:  # 如果料高超过限制，停止装料
            self.allow_plc_work = 0  # PLC停止
            self.flag_load = 0  # 装料机未装车
            self.work_weight_status = 2  # 作业已完成
            self.work_finish = 0  # 任务未完成
            self.load_time += (
                datetime.datetime.now()
                - self.load_start_time_list[self.icps_differ_index]
            )
            self.load_weight_end_list[self.icps_differ_index] = self.loadestimate
            remain_loadpoint = len(self.guide_position) - self.icps_differ_index - 1
            if remain_loadpoint > 0:
                self.logging.debug(
                    f"装料点[{self.guide_position[self.icps_differ_index]}]装料完毕, 后续还有{remain_loadpoint}个装料点"
                )
                self.icps_differ_index += 1
            else:
                self.logging.debug(
                    f"装料点[{self.guide_position[self.icps_differ_index]}]装料完毕, 后续没有装料点，任务结束!"
                )
                self.work_finish = 1  # 任务完成

    def sensor_status_ok(self, load_height) -> bool:
        if load_height is None:
            self.logging.debug("物位计无数据")
            self.allow_plc_work = 0
            self.work_finish = 0
            return False
        else:
            return True

    def get_sensor_data(self, reset=False) -> SensorData:
        if reset:
            self.load_height_queue = Queue(maxsize=20)
            self.load_height_list = list()
            self.load_height = SensorData(-1)
        load_height = self.Sensor.query.order_by(self.Sensor.id.desc()).first()
        if load_height is None:
            self.logging.debug("物位计无数据")
            self.allow_plc_work = 0
            self.work_finish = 0
            return SensorData(-1)
        else:
            load_height = load_height.data
            # 第一堆装料开始后，给第1个物位值，后面的物位值不能小于前一个物位值，如果小于，则物位值等于前一个物位值
            if (
                len(self.load_height_list) != 0
                and self.load_height_list[-1] > load_height
            ):
                load_height = self.load_height_list[-1]
                self.load_height.data = load_height

            # 如果前一个物位值和当前物位值相差大于0.02米，则约束为前一个物位值+0.02
            if (
                len(self.load_height_list) != 0
                and load_height - self.load_height_list[-1] > 0.03
            ):
                load_height = self.load_height_list[-1] + 0.01
                self.load_height.data = load_height

            if self.load_height_queue.full():
                self.load_height_queue.get()
            if self.allow_plc_work == 1:
                self.load_height_queue.put(load_height)
                self.load_height_list = list(self.load_height_queue.queue)
                self.logging.debug(f"load_height_list:{self.load_height_list}")
            return SensorData(load_height)

    # 获取上一车的装车数据
    def get_last_load_data(self):
        return {}

    # 获取调整系数
    def get_adjustment_co(self, co):
        return co

    # 预估重量6：用高度和时间同时估计
    def weight_estimate(
        self,
        goods_type,
        loader_id,
        opening_type,
        load_policy,
        load_height,
        load_weight_begin,
        load_height_begin,
    ) -> float:
        # 第1，2，3, ..., n堆
        current_load_weight = 0  # 当前载重量
        self.logging.debug(f"[weight_estimate] load_weight_begin:{load_weight_begin}")
        self.logging.debug(f"[weight_estimate] load_height_begin:{load_height_begin}")

        # 默认系数为1
        goods_co = self.GoodsCoefficient[goods_type].get(self.goods_source, 1)

        if load_height < 1:  # 503南物位计数据上窜下跳
            return 0

        if load_height_begin == 0:  # 有十条数据再开始估计重量
            return 0

        if load_policy == "h":  # 按高度估计策略
            if len(set(self.load_height_list)) == 1:
                self.logging.debug(
                    f"第{self.icps_differ_index + 1}堆料停止放料，记录停料时间"
                )
                # 一秒一个物位计数据
                if (
                    self.load_stop_time_list[self.icps_differ_index].total_seconds()
                    == 0
                ):
                    # 满足条件已经有10秒未下料
                    self.load_stop_time_list[self.icps_differ_index] = (
                        datetime.timedelta(seconds=10)
                    )
                else:
                    # 此后每次加一秒
                    self.load_stop_time_list[self.icps_differ_index] += (
                        datetime.timedelta(seconds=1)
                    )

            co11, co12, co13, co14 = self.LoadCoefficient[goods_type][opening_type][0]
            load_height_lift = load_height - load_height_begin
            if load_height_lift <= 0:
                current_load_weight = 0
            else:
                current_load_weight = (
                    co11 * load_height_lift**3
                    + co12 * load_height_lift**2
                    + co13 * load_height_lift
                    + co14
                )
                current_load_weight = (
                    current_load_weight * goods_co if current_load_weight >= 0 else 0
                )
            self.logging.debug(
                f"[delta_height >= 0.9] current_load_weight:{current_load_weight}"
            )
        elif load_policy == "t":  # 按时间估计策略
            loadn_usingheight = 0
            loadn_usingtime = 0
            current_load_weight_usingtime = self.loadestimate
            current_load_weight_usingheight = self.loadestimate

            # 第n堆参数和第一堆一样
            con1, con2, con3, con4 = self.LoadCoefficient[goods_type][opening_type][0]
            # 1. 计算初始高度重量
            load_heightn_lift_begin = load_height_begin - self.load_height_begin_list[0]
            load_weightn_begin = 0
            if load_heightn_lift_begin <= 0:
                load_weightn_begin = 0
            else:
                load_weightn_begin = (
                    con1 * load_heightn_lift_begin**3
                    + con2 * load_heightn_lift_begin**2
                    + con3 * load_heightn_lift_begin
                    + con4
                )
                load_weightn_begin = (
                    load_weightn_begin if load_weightn_begin >= 0 else 0
                )
            # 2. 计算当前高度重量
            load_heightn_lift_current = load_height - self.load_height_begin_list[0]
            load_weightn_current = 0
            if load_heightn_lift_current <= 0:
                load_weightn_current = 0
            else:
                load_weightn_current = (
                    con1 * load_heightn_lift_current**3
                    + con2 * load_heightn_lift_current**2
                    + con3 * load_heightn_lift_current
                    + con4
                )
                load_weightn_current = (
                    load_weightn_current if load_weightn_current >= 0 else 0
                )

            # 3. 步骤3 - 步骤2
            loadn_usingheight = load_weightn_current - load_weightn_begin
            current_load_weight_usingheight = (
                load_weight_begin + loadn_usingheight * goods_co
            )

            duration_heightn = (
                (
                    datetime.datetime.now()
                    - self.load_start_time_list[self.icps_differ_index]
                )
                - self.load_stop_time_list[self.icps_differ_index]
            ).total_seconds()  # 第2堆装料时间，秒

            # assert isinstance(self.load_time1, datetime.datetime)
            # 第一堆装料时间，考虑停料
            duration_height1 = (
                (self.load_time_list[0] - self.load_start_time)
                - self.load_stop_time_list[0]
            ).total_seconds()  # 第一堆装料时间，秒
            self.logging.debug(f"第一堆装料停料时间:{self.load_stop_time_list[0]}")
            self.logging.debug(f"第一堆装料时间:{duration_height1}")
            if duration_height1 > 0:  # 第一堆装料时间大于零
                discharge_speed = (
                    self.load_weight_end_list[0] / duration_height1
                )  # 放料速率，吨/秒
            else:
                discharge_speed = 0.035
            if discharge_speed < 0.035:
                discharge_speed = 0.035  # 假设第一堆中间有停料，给最小装料速度，估计
            elif discharge_speed > 0.07:
                discharge_speed = 0.07  # 按最快7分钟装25吨算
            self.logging.debug(f"放料速率:{discharge_speed}")
            loadn_usingtime = (
                float(duration_heightn) * discharge_speed
            )  # 按时间估计第2堆装料重量
            self.logging.debug(f"按物位估计重量:{loadn_usingheight}")
            self.logging.debug(f"按时间估计重量:{loadn_usingtime}")
            # 假设移车后60秒内料位不上升
            if duration_heightn <= 240:
                # 第2堆放料时间小于60秒且料高变化小于最小料高变化（60秒高度最小升高0.2)
                current_load_weight_usingtime = (
                    load_weight_begin + loadn_usingtime
                )  # 料位不变，按放料时间计算重量
            if duration_heightn > 240 and ((load_height - load_height_begin) < 0.0033):
                # 高度不变，时间大于1分钟，说明停料，增加的重量为0
                current_load_weight_usingtime = (
                    self.loadestimate
                )  # 增加重量为零（使用上一次估计的重量）

                self.load_stop_time_list[self.icps_differ_index] += datetime.timedelta(
                    seconds=1
                )  # 停料时间增加1秒
            self.logging.debug(
                f"current_load_weight_usingtime:{current_load_weight_usingtime}"
            )
            self.logging.debug(
                f"current_load_weight_usingheight:{current_load_weight_usingheight}"
            )
            if loadn_usingtime >= 0 and loadn_usingheight > 0:  # 高度和时间都有结果
                # 如果高度的结果大于时间的120%，小于时间的80%，用时间的结果；否则用高度的结果
                if (
                    current_load_weight_usingheight
                    > current_load_weight_usingtime * 1.2
                    or current_load_weight_usingheight
                    < current_load_weight_usingtime * 0.8
                ):
                    current_load_weight = current_load_weight_usingtime
                else:
                    # current_load_weight = current_load_weight_usingheight if current_load_weight_usingheight > current_load_weight_usingtime\
                    #     else current_load_weight_usingtime
                    current_load_weight = current_load_weight_usingtime
            else:
                current_load_weight = current_load_weight_usingtime
        return current_load_weight

    # FIXME: 待修改
    def manual_stop(self, auto_select):
        self.logging.debug(f"auto_select:{self.auto_select}")

        if auto_select == False:
            self.logging.debug(f"料高列表: {self.load_height_list}")
            self.logging.debug(
                f"在第{self.icps_differ_index + 1}个点位[{self.guide_position[self.icps_differ_index]}]手动停止"
            )
            return self.stop(self.truck_id, self.loader_id)

    # FIXME: 待修改
    def stop(self, truck_id, loader_id):
        self.logging.debug(f"truckid: {truck_id}")
        self.logging.debug(f"loaderid: {loader_id}")
        self.logging.debug("stop!")
        self.allow_plc_work = 0
        self.work_weight_status = 2
        self.load_end_time = self.load_start_time + timedelta(seconds=self.duration)
        self.loadstatus = "手动停止"
        for i in range(len(self.load_start_time_flag_list)):
            self.load_start_time_flag_list[i] = True
        from .socket import control_status_socket, loader_status_socket

        control_status_socket(
            {"value": self.allow_plc_work, "loaderid": self.loader_id}
        )
        loader_status_socket({"value": self.work_finish, "loaderid": self.loader_id})

        update_truck_content(
            truckid=self.truck_id,
            loaderid=self.loader_id,
            update_data={
                "loadendtime": self.load_end_time,
                "loadestimate": self.loadestimate,
                "loadstatus": self.loadstatus,
                "loadtimetotal": self.duration,
            },
        )
        self.logging.debug(f"loadendtime:{self.load_end_time}")
        self.logging.debug(f"duration:{self.duration}")

        result = gen_return_data(
            time=self.req_time,
            store_id=self.store_id,
            loader_id=self.loader_id,
            operating_stations={
                "truck_id": self.truck_id,
                "work_weight_status": self.work_weight_status,
                "work_weight_reality": self.loadestimate,
                "flag_load": self.flag_load,
                "height_load": self.height_load,
                "allow_plc_work": self.allow_plc_work,
                "work_finish": self.work_finish,
            },
        )

        return jsonify(result)

    def reconnectudp(self):
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.s.setblocking(False)

    def clearUDPBuffer(self):
        while True:
            try:
                buf = self.s.recv(4096)
            except BlockingIOError as b:
                break

    def print_current_policy(self) -> str:
        """
        打印当前策略
        :return:
        """
        if self.load_policy[self.icps_differ_index] == "h":
            current_policy = "height"
        elif self.load_policy[self.icps_differ_index] == "t":
            current_policy = "time"
        else:
            current_policy = "unknown"
        return current_policy


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
