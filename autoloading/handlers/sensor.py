import datetime
import logging
import socket, time
import struct
from .socket import sensor_data

from autoloading.models import db


def read_per_second(loadpoint):  # 每秒读取一次物位
    # while True:
        # 任务开始时间
        # start_time = time.perf_counter()

        int_distance = 0
        # current_time = datetime.datetime.now() # 获取当前时间作为读取物位计数据的时间(有一定的延迟)

        received_data = -1

        #发送modbus指令，接受数据

        try:
            loadpoint.s.sendto(loadpoint.byte_data, loadpoint.server_ip)
        except socket.error as e:
        # FIXME: 检查错误码e
            # logging.debug(f'错误码e:{e}')
            return
        try:
            received_data, addr = loadpoint.s.recvfrom(1024)
        except socket.error as e:
            return

        # 接收数据时间
        # receive_time = time.perf_counter()

        # FIXME: 打印原始数据
        # logging.debug(f'received_data: {received_data}')
        hex_received_data = received_data.hex()   # 将原始数据转换成16进制

        if len(hex_received_data) != 18:   # 筛选长度不满18的数据，防止错误数据干扰
            return
        # logging.debug(f'hex_received_data: {hex_received_data}')
        hex_distance = hex_received_data[6:14]  # 数据切片，获取表示距离的数据
        # logging.debug(f'hex_distance: {hex_distance}')
        int_ma = int(hex_distance, 16)
        # 交换高16位和低16位的数据
        swapped_ma = (int_ma & 0xFFFF0000) >> 16 | (int_ma & 0x0000FFFF) << 16
        # 将结果转换回十六进制字符串
        hex_num = format(swapped_ma, '08X')
        float_hex = struct.unpack('!f', bytes.fromhex(hex_num))[0]
        int_distance = round(float_hex*1.0,3)  # 数据保留3位小数
        current_time = datetime.datetime.now()
        
        # logging.debug(f'int_distance: {int_distance}')
        # latest_data = loadpoint.Sensor.query.order_by(loadpoint.Sensor.id.desc()).first()
        # 将数据存入数据库中并发送至前端(如果数据库中无数据或者当前数据获取时间比数据库中数据获取时间晚1s)
        # if (latest_data is None) or ((current_time - latest_data.time).total_seconds() > 1): 
        
        # logging.debug(f'{loadpoint.Sensor.__tablename__}: {int_distance}')


        # 发送物位计数据到前端
        sensor_data({
            'value': int_distance,
            'tablename': loadpoint.Sensor.__tablename__
        })
        loadpoint.reconnectudp()
        # time.sleep(1)  # 1s获取一次数据


       # 存储数据前时间
        # upload_time = time.perf_counter()

        if int_distance > 0.02:
            insert_data(loadpoint.Sensor,int_distance, current_time)

        # 存储数据后时间
        # afterload_time = time.perf_counter()

        # insert_time = afterload_time - upload_time
        # print(f"{loadpoint.Sensor.__tablename__}:数据库插入耗时{insert_time*1000:.3f}毫秒")

        # 任务结束时间
        # end_time = time.perf_counter()

        # execution_time = end_time - start_time
        # print(f"任务执行耗费{execution_time*1000:.3f}毫秒")


# 将测量值和时间存储在数据库中
def insert_data(Sensor,int_distance, current_time):
    sensor = Sensor(data=int_distance, time=current_time, tablename=Sensor.__tablename__)
    db.session.add(sensor)
    db.session.commit()

