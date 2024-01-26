import datetime
import logging
import socket, time
import struct

from autoloading.models import db

from autoloading.config import SHOW_TAB

int_distance = 0
current_time = 0


def read_per_second(loadpoint):  # 每秒读取一次物位计数据

    global int_distance
    global current_time
    global SHOW_TAB
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
    hex_received_data = received_data.hex()
    if len(hex_received_data) != 18:
        return
    # FIXME: 打印hex数据
    # logging.debug(f'hex_received_data: {hex_received_data}')
    current_time = datetime.datetime.now()
    hex_distance = hex_received_data[6:14]
    # FIXME: 打印截取数据位
    # logging.debug(f'hex_distance: {hex_distance}')
    int_ma = int(hex_distance, 16)
    # 交换高16位和低16位的数据
    swapped_ma = (int_ma & 0xFFFF0000) >> 16 | (int_ma & 0x0000FFFF) << 16
    # 将结果转换回十六进制字符串
    hex_num = format(swapped_ma, '08X')
    float_hex = struct.unpack('!f', bytes.fromhex(hex_num))[0]
    int_inch=float_hex*2.54*10 # 假設是英寸，轉換成毫米
    # FIXME: 打印转换数值
    # logging.debug(f'int_inch: {int_inch}')
    result = round(int_inch * 1, 0)
    int_distance = result#int(result)
    # FIXME: 打印取整结果
    # logging.debug(f'int_distance: {int_distance}')
    latest_data = loadpoint.Sensor.query.order_by(loadpoint.Sensor.id.desc()).first()
    if (latest_data is None) or ((current_time - latest_data.time).total_seconds() > 1):
        insert_data(loadpoint.Sensor,int_distance, current_time)

    # FIXME: 查看当前页面对应的数据表名
    # logging.debug(f'show_tab: {SHOW_TAB.queue}')
    # 发送物位计数据到前端
    if loadpoint.Sensor.__tablename__ in SHOW_TAB.queue:
        sensor_data({
            'value': int_distance
        })

# 将测量值和时间存储在数据库中
def insert_data(Sensor,int_distance, current_time):
    # FIXME: 查看插入数据
    # logging.debug(f'before inserting data:{int_distance}')
    # XXX:滤波，至少5个数据（线性变化，
    #if int_distance > 0.8:  # 确保存入有效数据
    sensor = Sensor(data=int_distance, time=current_time)
    db.session.add(sensor)
    db.session.commit()

