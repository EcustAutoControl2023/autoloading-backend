import json
import time

import requests
#import yaml

#0、 将任务信息传给时庐获取引导策略
data1 = {
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
# 1、 集卡引导到位，获取时庐的PLC控制策略
data2 = {
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

# 2、向时庐平台反馈出闸信息
data3 = {
    "data_type": 2,
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
        "truck_weight_out": 30,
        "goods_type": "木片",
        "store_id": 1,
        "loader_id": 20
    }
}
# 3、请求实时作业情况（心跳）
data4 = {
    "data_type": 3,
    "time": "2023/4/10 2:26:16",
    "operating_stations": {
        "store_id": 1,
        "loader_id": 20,
        #"breakdowncode": 2012
    }
    
}
# 4、OCR识别错误弹窗进行人工确认
data5 = {
    "data_type": 4,
    "time": "2023/4/10 2:26:16",
    "operating_stations": {
        "truck_id": "闽D123456",
        "store_id": 1,
        "loader_id": 20,
        "picture_url_plate": "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    }
}

url = 'localhost:8000/connect'
r1 = requests.post(url, json=data1).json()
print(r1)

# 第1辆装料2堆，时间为9:50-9:56,9:57-10:00

truck1_type0 = {
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

truck1_type1 = {
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


url = 'localhost:8000/connect'
r1 = requests.post(url, json=truck1_type0).json()
print(r1)