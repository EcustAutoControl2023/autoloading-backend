from queue import Queue
import ast
import datetime
import time
import json
from pytest_bdd import scenarios, given, when, then, parsers, scenario
from autoloading.handlers.loaderpoint import LoadPoint
from autoloading.models.sensor import Traffic
from .conftest import printr, udp_client

# scenarios("feature/connect.feature")


"""
Scenario Outline: 2.1.1 将任务信息传给时庐获取引导策略
"""
@given(parsers.parse("测试的post文件为: {file}"), target_fixture="jsondata", converters={"file": str})
def jsondata(file):
    with open(file, encoding="utf8") as json_file:
        jsondata = json.load(json_file)
    return jsondata

@given(parsers.parse("三个装料点位: {distance_0}, {distance_1}, {distance_2}"),
       converters={
           "distance_0": float,
           "distance_1": float,
           "distance_2": float
       })
def clientdata(jsondata, distance_0, distance_1, distance_2):
    printr((distance_0, distance_1, distance_2))
    jsondata['operating_stations']['distance_0'] = distance_0
    jsondata['operating_stations']['distance_1'] = distance_1
    jsondata['operating_stations']['distance_2'] = distance_2

@when("客户端发送post请求data_type=0", target_fixture='response0')
def post0(client, jsondata):
    jsondata["data_type"] = 0
    printr(jsondata)
    response = client.post("/connect", json=jsondata)
    return response

@when("根据装料点位发送post请求data_type=1", target_fixture='response1')
def post1(client, jsondata):
    wait_time = jsondata.get("delay_send")
    printr(wait_time, "wait_time")
    jsondata["data_type"] = 1
    printr(jsondata)
    distance_0 = jsondata['operating_stations']['distance_0']
    distance_1 = jsondata['operating_stations']['distance_1']
    distance_2 = jsondata['operating_stations']['distance_2']
    if (distance_0 != distance_1) and (distance_0 != distance_2) and (distance_1 != distance_2):
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        time.sleep(wait_time)
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_1
        time.sleep(wait_time)
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_2
        jsondata["operating_stations"]["temp_manual_stop"] = jsondata["temp_manual_stop"]
    elif (distance_0 == distance_1) and (distance_1 != distance_2) :
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        time.sleep(wait_time)
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_2
        jsondata["operating_stations"]["temp_manual_stop"] = jsondata["temp_manual_stop"]
    elif (distance_1 == distance_2) and (distance_1 != distance_0) :
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        time.sleep(wait_time)
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_1
        jsondata["operating_stations"]["temp_manual_stop"] = jsondata["temp_manual_stop"]
    elif (distance_0 == distance_1) and (distance_1== distance_2) :
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        jsondata["operating_stations"]["temp_manual_stop"] = jsondata["temp_manual_stop"]
    else:
        jsondata["operating_stations"]["icps_differ_current"] = None
        jsondata["operating_stations"]["temp_manual_stop"] = jsondata["temp_manual_stop"]

    time.sleep(wait_time)
    response = client.post("/connect", json=jsondata)
    return response

@then(parsers.parse("返回正确的装车策略: {expected_icps_differ}"))
def check_strategy_0(app, db, response0, expected_icps_differ):
    # 确保后端无逻辑错误
    assert response0.status_code == 200

    responsedata = json.loads(response0.data)

    # 确保返回参数符合要求
    assert "time" in responsedata.keys()
    assert "store_id" in responsedata.keys()
    assert "loader_id" in responsedata.keys()
    assert "operating_stations" in responsedata.keys()
    assert "truck_id" in responsedata.get('operating_stations').keys()
    assert "icps_differ" in responsedata.get('operating_stations').keys()
    actual_icps_differ = responsedata.get('operating_stations').get('icps_differ')
    if actual_icps_differ is None:
        actual_icps_differ = "None"
    assert str( actual_icps_differ ) == expected_icps_differ

    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 1

"""
END
"""

"""
2.1.1 将任务信息传给时庐获取引导策略——异常测试(data_type=1未收到结束或移动点位响应，但请求data_type=0)
"""
@then(parsers.parse("返回错误的装车策略: {expected_icps_differ}"))
def check_strategy_0_exception(app, db, response0, expected_icps_differ):
    # 确保后端无逻辑错误
    assert response0.status_code == 200

    responsedata = json.loads(response0.data)

    # 确保返回参数符合要求
    actual_icps_differ = responsedata.get('operating_stations').get('icps_differ')
    if actual_icps_differ is None:
        actual_icps_differ = "None"
    assert str( actual_icps_differ ) == expected_icps_differ

    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 1
"""
END
"""

"""
2.1.2 集卡引导到位，获取时庐的 PLC 控制策略
"""

@given(parsers.parse("模拟的装车数据: {csv_file}"), converters={"csv_file": str})
def send_scv(csv_file, jsondata):
    loader_id = jsondata.get("operating_stations").get("loader_id")
    # printr(jsondata)
    # printr(loader_id, "loader_id")
    serverInfo = LoadPoint.ServerList[LoadPoint.loader_index_dict[loader_id]]
    printr(serverInfo, "ipport")
    udp_client(serverInfo=serverInfo, send_data=csv_file)

@when("创建生成器: 模拟客户端发送post请求data_type=1", target_fixture="gen_post")
def post_generator(client, jsondata):
    jsondata["data_type"] = 1
    def gen_post(client, jsondata):
        while True:
            printr(jsondata, "jsondata")
            response = client.post("/connect", json=jsondata)
            yield response
            josnresponse = json.loads(response.data)
            printr(josnresponse, "josnresponse")
            if josnresponse.get("operating_stations").get("work_finish") == 1:
                break
    return gen_post(client, jsondata)

@then(parsers.parse("使用生成器模拟请求，返回正确的装车策略直至装车停止: {expected_return_file}"))
def check_strategy_1(app, db, gen_post, expected_return_file):
    # 等待数据库中有传感器数据（新数据库最开始没有数据）
    time.sleep(1.1)
    responsedata = dict()
    for response in gen_post:
        with app.app_context():
            traffics = db.session.query(Traffic).all()
            assert len(traffics) == 1
            assert response.status_code == 200
            responsedata = json.loads(response.data)

            # 确保返回参数符合要求
            assert "time" in responsedata.keys()
            assert "store_id" in responsedata.keys()
            assert "loader_id" in responsedata.keys()
            assert "operating_stations" in responsedata.keys()
            assert "truck_id" in responsedata.get('operating_stations').keys()
            assert "work_weight_status" in responsedata.get('operating_stations').keys()
            assert "work_weight_reality" in responsedata.get('operating_stations').keys()
            assert "flag_load" in responsedata.get('operating_stations').keys()
            assert "height_load" in responsedata.get('operating_stations').keys()
            assert "allow_plc_work" in responsedata.get('operating_stations').keys()
            assert "work_finish" in responsedata.get('operating_stations').keys()

        # 假设客户端每隔1s请求一次装车策略
        time.sleep(1)
    printr(responsedata, "final-response")

"""
END
"""

"""
2.1.2 集卡引导到位，获取时庐的 PLC 控制策略——异常测试(未请求data_type=0)
"""
@when("客户端发送post请求data_type=1", target_fixture='response1')
def response(client, jsondata):
    jsondata["data_type"] = 1
    response = client.post("/connect", json=jsondata)
    return response

@then(parsers.parse("返回错误的料高: {expected_height_load:d}"))
def check_strategy_1_error(app, db, response1, expected_height_load):
    # 确保后端无逻辑错误
    assert response1.status_code == 200

    responsedata = json.loads(response1.data)

    # 确保返回参数符合要求
    actual_height_load = responsedata.get('operating_stations').get('height_load')
    assert expected_height_load == actual_height_load

    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 0
"""
END
"""

@given("初始化")
def init(jsondata):
    # 默认延迟发送时间为0
    jsondata["delay_send"] = 0
    # 默认手动停止为0
    jsondata["temp_manual_stop"] = 0

@given(parsers.parse("等待{time:d}秒"), target_fixture='wait_time')
def wait_time(time):
    return time

@when(parsers.parse("手动停止"))
def temp_manual_stop(jsondata):
    jsondata["temp_manual_stop"] = 1

@when(parsers.parse("延迟发送"))
def delay_send(jsondata, wait_time):
    jsondata["delay_send"] = wait_time

@then(parsers.parse("返回正确的装车时间: {expected_duration:d}"))
def check_strategy_1_duration(app, db, response1, expected_duration):
    # 确保后端无逻辑错误
    assert response1.status_code == 200

    loader_id = response1.json.get('loader_id')

    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 1
        printr(traffics[0].loadtimetotal, "loadtimetotal")
        printr(expected_duration, "expected_duration")
        actual_duration = traffics[0].loadtimetotal
        time_diff = abs(expected_duration - actual_duration)
        assert time_diff < 1

"""
END
"""

"""
Scenario Outline: 2.1.3 装车完成后，获取出闸重量
"""
@given(parsers.parse("模拟出闸量: {weight_out:d}"), target_fixture="weight_out")
def weight_out(weight_out):
    return weight_out

@when("客户端发送post请求data_type=2", target_fixture='response2')
def post2(client, jsondata):
    jsondata["data_type"] = 2
    # printr(jsondata)
    response = client.post("/connect", json=jsondata)
    return response

@then(parsers.parse("返回正确的出闸重量: {expected_weight_out:d}"))
def check_weight_out(app, db, response2, expected_weight_out):
    # 确保后端无逻辑错误
    assert response2.status_code == 200

    responsedata = json.loads(response2.data)
    truck_id = responsedata.get('operating_stations').get('truck_id')
    printr(truck_id, "truck_id2")
    traffic = Traffic.query.filter_by(truckid=truck_id).first()

    actual_weight_out = traffic.truckweightout

    assert actual_weight_out == expected_weight_out

    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 1
"""
END
"""

"""
  Scenario Outline: 2.1.3 两辆车装车完成后，合作方提供第一辆的出闸重量
"""
@given(parsers.parse("车辆队列: {truck_id}"), target_fixture="truck_id_queue")
def truck_id_queue(truck_id):
    truck_id = ast.literal_eval(truck_id)
    truck_id_queue = Queue(maxsize=len(truck_id))
    for i in truck_id:
        truck_id_queue.put(i)
    return truck_id_queue

@given(parsers.parse("模拟出闸量队列: {weight_out}"), target_fixture="weight_out_queue")
def weight_out_queue(weight_out):
    weight_out = ast.literal_eval(weight_out)
    weight_out_queue = Queue(maxsize=len(weight_out))
    for i in weight_out:
        weight_out_queue.put(i)
    return weight_out_queue

@when("车牌变更")
def change_truck_id(jsondata, truck_id_queue):
    jsondata["operating_stations"]["truck_id"] = truck_id_queue.get()

@when("出闸")
def change_weight_out(jsondata, weight_out_queue):
    jsondata["operating_stations"]["truck_weight_out"] = weight_out_queue.get()

@scenario("./feature/connect.feature", "2.1.1 将任务信息传给时庐获取引导策略")
def test_data_type0():
    pass

@scenario("./feature/test.feature", "一次装料，记录时间")
def test_load_once():
    pass

@scenario("./feature/connect.feature", "2.1.3 装车完成后，获取出闸重量")
def test_data_type2():
    pass

@scenario("./feature/connect.feature", "2.1.3 两辆车装车完成后，合作方提供第一辆的出闸重量")
def test_two_truck():
    pass

@scenario("./feature/connect.feature", "2.1.1 将任务信息传给时庐获取引导策略——异常测试(data_type=1未收到结束或移动点位响应，但请求data_type=0)")
def test_data_type0_exception():
    pass

# @scenario("./feature/connect.feature", "2.1.2 集卡引导到位，获取时庐的 PLC 控制策略")
# def test_data_type1():
#     pass

@scenario("./feature/connect.feature", "2.1.2 集卡引导到位，获取时庐的 PLC 控制策略——异常测试(未请求data_type=0)")
def test_data_type1_exception():
    pass
