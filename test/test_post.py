import json
import time

import requests

# 第1辆装料2堆，时间为9:50-9:56,9:57-10:00

truck1_type0 = {
    "data_type": 0,
    "time": "2023/10/20 9:26:16",
    "operating_stations": {
        "job_id": "123456",
        "truck_id": "闽D123456",
        "box_length": 10.2,
        "box_width": 5.6,
        "box_height": 2.8,
        "distance_0": 1.1,
        "distance_1": 1.1,
        "distance_2": 2.3,
        "truck_load": 40.2,
        "load_current": 20.6,
        "truck_weight_in": 20,
        "goods_type": "木片",
        "store_id": 1,
        "loader_id": 20,
        "picture_url_plate": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    }
}

truck1_type1 = {
    "data_type": 1,
    "time": "2023/4/10 2:26:16",
    "operating_stations": {
        "job_id": "123456",
        "truck_id": "闽D123456",
        "box_length": 10.2,
        "box_width": 5.6,
        "box_height": 2.8,
        "distance_0": 1.1,
        "distance_1": 1.1,
        "distance_2": 2.3,
        "truck_load": 40.2,
        "load_current": 20.6,
        "truck_weight_in": 20,
        "goods_type": "木片",
        "store_id": 1,
        "loader_id": 20,
        "picture_url_plate": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png",
        "picture_url_request": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    }
}

# 第2辆10:03-10:10，装料1堆

truck2_type0 = {
    "data_type": 0,
    "time": "2023/4/10 2:26:16",
    "operating_stations": {
        "job_id": "123456",
        "truck_id": "闽D123456",
        "box_length": 10.2,
        "box_width": 5.6,
        "box_height": 2.8,
        "distance_0": 1.1,
        "distance_1": 1.1,
        "distance_2": 1.1,
        "truck_load": 40.2,
        "load_current": 20.6,
        "truck_weight_in": 20,
        "goods_type": "木片",
        "store_id": 1,
        "loader_id": 20,
        "picture_url_plate": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    }
}

truck2_type1 = {
    "data_type": 1,
    "time": "2023/4/10 2:26:16",
    "operating_stations": {
        "job_id": "123456",
        "truck_id": "闽D123456",
        "box_length": 10.2,
        "box_width": 5.6,
        "box_height": 2.8,
        "distance_0": 1.1,
        "distance_1": 1.1,
        "distance_2": 1.1,
        "truck_load": 40.2,
        "load_current": 20.6,
        "truck_weight_in": 20,
        "goods_type": "木片",
        "store_id": 1,
        "loader_id": 20,
        "picture_url_plate": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png",
        "picture_url_request": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    }
}

# 第3辆装料29吨，装料2堆，10:28-10:35,10:35-10:38

truck3_type0 = {
    "data_type": 0,
    "time": "2023/4/10 2:26:16",
    "operating_stations": {
        "job_id": "123456",
        "truck_id": "闽D123456",
        "box_length": 10.2,
        "box_width": 5.6,
        "box_height": 2.8,
        "distance_0": 2.3,
        "distance_1": 1.1,
        "distance_2": 1.1,
        "truck_load": 40.2,
        "load_current": 20.6,
        "truck_weight_in": 20,
        "goods_type": "木片",
        "store_id": 1,
        "loader_id": 20,
        "picture_url_plate": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    }
}

truck3_type1 = {
    "data_type": 1,
    "time": "2023/4/10 2:26:16",
    "operating_stations": {
        "job_id": "123456",
        "truck_id": "闽D123456",
        "box_length": 10.2,
        "box_width": 5.6,
        "box_height": 2.8,
        "distance_0": 2.3,
        "distance_1": 1.1,
        "distance_2": 1.1,
        "truck_load": 40.2,
        "load_current": 20.6,
        "truck_weight_in": 20,
        "goods_type": "木片",
        "store_id": 1,
        "loader_id": 20,
        "picture_url_plate": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png",
        "picture_url_request": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    }
}
#print(r5)
# print(str(r1))
#with open('./test.yml', 'w', encoding='utf-8') as f:
#    yaml.dump_all(documents=[r1, r2, r3, r4, r5], stream=f, allow_unicode=True)


# 将策略写入文件


with open('./test_1020_1032.txt', 'w', encoding='utf-8') as f:
    url = 'http://127.0.0.1:8000/connect'
    r1 = requests.post(url, json=truck3_type0).json() # 获取装车策略
    f.write(str(r1))
    # 分割线
    f.write('\n')

    if r1 is not None:
        r2 = requests.post(url, json=truck3_type1).json() # 获取控制策略
        f.write('==============\n\n 第一堆料装料！\n\n=========')
        while r2['operating_stations']['allow_plc_work'] == 1: # 持续装料，等待第一堆料装料完毕
            r2 = requests.post(url, json=truck3_type1).json() 
            f.write(str(r2))
            f.write('\n')
            time.sleep(2) # 每隔2s获取一次装料机控制策略
        f.write(str(r2))
        time.sleep(90) # 货车移动时间
        if r2['operating_stations']['work_finish'] == 0: # 如果装完一堆料以后还需要装料，则获取第二堆料的控制策略
            f.write('==============\n\n 第二堆料装料！\n\n=========')
            r3 = requests.post(url, json=truck3_type1).json()
            f.write(str(r3))
            while r3['operating_stations']['allow_plc_work'] == 1: # 等待第二堆料装料完毕
                r3 = requests.post(url, json=truck3_type1).json()
                f.write(str(r3))
                time.sleep(2)
            f.write(str(r3))
        else:
            pass
