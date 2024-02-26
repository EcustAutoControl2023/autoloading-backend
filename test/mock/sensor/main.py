import struct
import socket
import pandas as pd
import random
import time


def read_from_csv(filepath):
    # 读取模拟的装车传感器数据
    sdata = pd.read_csv(filepath)

    # 数据生成器
    def gen_data(sdata: pd.DataFrame):
        sdata_step = 0
        sdata_len = len(sdata) - 1
        while True:
            distance = sdata.iloc[sdata_step]['data']
            sdata_step += 1
            if sdata_step > sdata_len:
                sdata_step = 0
            # 将整数转换为16进制字符串
            print(f'original data: {distance}')
            byte_data = struct.pack('!f', distance)
            # print(f'byte_data: {byte_data}')
            byte_data = byte_data[2:4] + byte_data[0:2]
            # print("转换为字节数据:", byte_data)
            ret = b'\1\4\4' + byte_data + b'\1\1'
            print("转换为字节数据:", ret)
            yield ret

    return gen_data(sdata=sdata)


def init_udp_server(server, host, port):
    server.bind((host, port))
    print("UDP 服务端已启动")

def start_listening(server):
    # 测试启动条件
    def get_csv_file(msg)->bool:
        if ".csv" in msg:
            return True
        return False

    msg = ''
    gen = ''

    while True:
        # 等待启动条件
        while True:
            data, addr = server.recvfrom(1024)
            print(f"接收到来自 {addr} 的数据: {data.decode()}")
            server.sendto(b'3q', addr)
            msg = data.decode()
            if get_csv_file(msg=msg):
                gen = read_from_csv(msg)
                msg = ''
                break
            time.sleep(1)

        # 模拟传感器
        while True:
            data, addr = server.recvfrom(1024)
            print(f"接收到来自 {addr} 的数据: {data.decode()}")
            msg = data.decode()
            # 回复数据
            server.sendto(gen.__next__(), addr)
            if get_csv_file(msg=msg):
                gen = read_from_csv(msg)
                msg = ''

def release_udp_server(server):
    server.close()

def simulate_intermittent_crash():
    # 模拟间歇性死机
    if random.random() < 0.3:
        print("模拟间歇性死机")
        time.sleep(10)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    init_udp_server(server, "0.0.0.0", 8234)
    start_listening(server=server)
    release_udp_server(server=server)
