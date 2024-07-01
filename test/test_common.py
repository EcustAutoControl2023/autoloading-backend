import ast
import datetime
import json
from pytest_bdd import given, when, then, parsers
from autoloading.handlers.loaderpoint import LoadPoint
from autoloading.models.sensor import Traffic
from .conftest import printr, udp_client


"""
==============================================
===============data_type=0====================
==============================================
"""

@given(parsers.parse("测试的post文件: {file}"), target_fixture="postdata", converters={"file": str})
def postdata(file):
    with open(file, encoding="utf8") as post_file:
        postdata = json.load(post_file)
    printr(postdata, "postdata -> origin")
    return postdata

@given("初始化post数据")
def init_post_data(postdata): # 初始化测试变量，仅在测试中使用
    # 默认延迟发送时间为0
    postdata["delay_send"] = 0
    # 默认手动停止为0
    postdata["temp_manual_stop"] = 0
    # 随机车牌号
    postdata['operating_stations']['truck_id'] = "test" + str(datetime.datetime.now().timestamp())

@given(parsers.parse("装料点位: {distance_list}"), target_fixture="distance_list", converters={"distance_list": ast.literal_eval})
def clientdata(postdata, distance_list:list):
    printr(distance_list, "distance_list")
    postdata['operating_stations']['distance_0'] = distance_list[0] if len(distance_list) > 0 else None
    postdata['operating_stations']['distance_1'] = distance_list[1] if len(distance_list) > 1 else None
    postdata['operating_stations']['distance_2'] = distance_list[2] if len(distance_list) > 2 else None
    distance_list = list(dict.fromkeys(distance_list))
    return distance_list

@when("手动停止模式")
def temp_manual_stop(postdata):
    postdata["temp_manual_stop"] = 1

def check_response(response, data_type):
    assert response.status_code == 200
    responsedata = json.loads(response.data)
    assert "time" in responsedata.keys()
    assert "store_id" in responsedata.keys()
    assert "loader_id" in responsedata.keys()
    assert "operating_stations" in responsedata.keys()
    assert "truck_id" in responsedata.get('operating_stations').keys()
    if data_type == 0:
        assert "icps_differ" in responsedata.get('operating_stations').keys()
        assert "work_finish" in responsedata.get('operating_stations').keys()
    elif data_type == 1 or data_type == 3:
        assert "work_weight_status" in responsedata.get('operating_stations').keys()
        assert "work_weight_reality" in responsedata.get('operating_stations').keys()
        assert "flag_load" in responsedata.get('operating_stations').keys()
        assert "height_load" in responsedata.get('operating_stations').keys()
        assert "allow_plc_work" in responsedata.get('operating_stations').keys()
        assert "work_finish" in responsedata.get('operating_stations').keys()
    elif data_type == 2:
        assert "work_total" in responsedata.get('operating_stations').keys()
    elif data_type == 4:
        pass

    return responsedata


"""
==============================================
===============data_type=1====================
==============================================
"""

@given(parsers.parse("模拟的装车数据: {csv_file}"), converters={"csv_file": str})
def send_scv(csv_file, postdata):
    loader_id = postdata.get("operating_stations").get("loader_id")
    serverInfo = LoadPoint.ServerList[LoadPoint.loader_index_dict[loader_id]]
    printr(serverInfo, "ipport")
    udp_client(serverInfo=serverInfo, send_data="restart")
    udp_client(serverInfo=serverInfo, send_data=csv_file)

@when("模拟装车模式", target_fixture="gen_post")
def post_generator(client, postdata):

    postdata["data_type"] = 1
    def gen_post(client, postdata):
        while True:
            printr(postdata, "postdata -> datatype=1")
            response = client.post("/connect", json=postdata)
            yield response
            josnresponse = json.loads(response.data)
            printr(josnresponse, "response -> datatype=1")
            if josnresponse.get("operating_stations").get("work_finish") == 1:
                break
    return gen_post(client, postdata)
