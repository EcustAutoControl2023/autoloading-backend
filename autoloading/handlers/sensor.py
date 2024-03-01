import datetime
import logging
import socket, time
import struct

from autoloading.models import db


def read_per_second(loadpoint):  # 每秒读取一次物位计数据

    int_distance = 0
    # current_time = datetime.datetime.now() # 获取当前时间作为读取物位计数据的时间(有一定的延迟)
    from .socket import sensor_data

    received_data = -1

    #发送modbus指令，接受数据
    while True:
        try:
            loadpoint.s.sendto(loadpoint.byte_data, loadpoint.server_ip)
        except socket.error as e:
            # FIXME: 检查错误码e
            # logging.debug(f'错误码e:{e}')
            continue
        break

    send_time = datetime.datetime.now()

    while True:
        try:
            received_data, addr = loadpoint.s.recvfrom(1024)
        except socket.error as e:
            delta_time = datetime.datetime.now() - send_time
            # FIXME: 打印连接时间间隔
            # logging.debug(f'delta_time{delta_time.total_seconds()}')
            if delta_time.total_seconds() > 1:
                return
            continue
        break

    # FIXME: 打印原始数据
    # logging.debug(f'received_data: {received_data}')
    hex_received_data = received_data.hex()   # 将原始数据转换成16进制
    if len(hex_received_data) != 18:   # 筛选长度不满18的数据，防止错误数据干扰
        return
    # logging.debug(f'hex_received_data: {hex_received_data}')
    current_time = datetime.datetime.now()
    hex_distance = hex_received_data[6:14]  # 数据切片，获取表示距离的数据
    # logging.debug(f'hex_distance: {hex_distance}')
    int_ma = int(hex_distance, 16)
    # 交换高16位和低16位的数据
    swapped_ma = (int_ma & 0xFFFF0000) >> 16 | (int_ma & 0x0000FFFF) << 16
    # 将结果转换回十六进制字符串
    hex_num = format(swapped_ma, '08X')
    float_hex = struct.unpack('!f', bytes.fromhex(hex_num))[0]
    int_distance = round(float_hex*1.0,3)  # 数据保留3位小数
    # logging.debug(f'int_distance: {int_distance}')
    latest_data = loadpoint.Sensor.query.order_by(loadpoint.Sensor.id.desc()).first()
    # 将数据存入数据库中并发送至前端(如果数据库中无数据或者当前数据获取时间比数据库中数据获取时间晚1s)
    if (latest_data is None) or ((current_time - latest_data.time).total_seconds() > 1): 
        insert_data(loadpoint.Sensor,int_distance, current_time)

        # 发送物位计数据到前端
        sensor_data({
            'value': int_distance,
            'tablename': loadpoint.Sensor.__tablename__
        })

# 将测量值和时间存储在数据库中
def insert_data(Sensor,int_distance, current_time):
    if int_distance > 0.02:  # 确保存入有效数据
        sensor = Sensor(data=int_distance, time=current_time, tablename=Sensor.__tablename__)
        db.session.add(sensor)
        db.session.commit()

