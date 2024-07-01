import struct
import socket
import pandas as pd
import random
import time

flag = -1 # 0: 正常，等待提供csv文件；1:重启；2:服务停止；3:数据传输


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
    global flag
    # 测试启动条件
    def get_csv_file(msg)->bool:
        if ".csv" in msg:
            return True
        return False

    csv = ''
    gen = ''

    while True:
        data, addr = server.recvfrom(1024)
        print(f"接收到来自 {addr} 的数据: {data.decode()}")
        recv_data = data.decode()
        if recv_data == 'start': # 等待启动条件
            flag = 0
            continue
        elif recv_data == 'restart':
            if flag == -1:
                flag = 0
                continue
            flag = 1
        elif recv_data == 'stop':
            flag = 2

        if flag == 0:
            # data, addr = server.recvfrom(1024)
            print(f"接收到来自 {addr} 的CSV文件: {recv_data}")
            csv = recv_data
            server.sendto(b'3q', addr)
            if get_csv_file(msg=csv):
                gen = read_from_csv(csv)
                # break
            flag = 3
            time.sleep(1)
        elif flag == 1:
            if get_csv_file(msg=csv):
                gen = read_from_csv(csv)
            flag = 3
        elif flag == 2:
            break
        elif flag == 3: # 模拟传感器
            # data, addr = server.recvfrom(1024)
            print(f"接收到来自 {addr} 的数据: {recv_data}")
            # 回复数据
            server.sendto(gen.__next__(), addr)

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
