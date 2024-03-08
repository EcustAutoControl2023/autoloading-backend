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
    with open(file) as json_file:
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

@when("客户端发送post请求data_type=0", target_fixture='response')
def post0(client, jsondata):
    jsondata["data_type"] = 0
    printr(jsondata)
    response = client.post("/connect", json=jsondata)
    return response

@when("根据装料点位发送post请求data_type=1")
def post1(client, jsondata):
    jsondata["data_type"] = 1
    printr(jsondata)
    distance_0 = jsondata['operating_stations']['distance_0']
    distance_1 = jsondata['operating_stations']['distance_1']
    distance_2 = jsondata['operating_stations']['distance_2']
    if (distance_0 != distance_1) and (distance_0 != distance_2) and (distance_1 != distance_2):
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_1
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_2
        jsondata["operating_stations"]["temp_manual_stop"] = 1
        response = client.post("/connect", json=jsondata)
    elif (distance_0 == distance_1) and (distance_1 != distance_2) :
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_2
        jsondata["operating_stations"]["temp_manual_stop"] = 1
        response = client.post("/connect", json=jsondata)
    elif (distance_1 == distance_2) and (distance_1 != distance_0) :
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        response = client.post("/connect", json=jsondata)
        jsondata["operating_stations"]["icps_differ_current"] = distance_1
        jsondata["operating_stations"]["temp_manual_stop"] = 1
        response = client.post("/connect", json=jsondata)
    elif (distance_0 == distance_1) and (distance_1== distance_2) :
        jsondata["operating_stations"]["icps_differ_current"] = distance_0
        jsondata["operating_stations"]["temp_manual_stop"] = 1
        response = client.post("/connect", json=jsondata)
    else:
        jsondata["operating_stations"]["icps_differ_current"] = None
        jsondata["operating_stations"]["temp_manual_stop"] = 1
        response = client.post("/connect", json=jsondata)
    return response

@then(parsers.parse("返回正确的装车策略: {expected_icps_differ}"))
def check_strategy_0(app, db, response, expected_icps_differ):
    # 确保后端无逻辑错误
    assert response.status_code == 200

    responsedata = json.loads(response.data)

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
def check_strategy_0_exception(app, db, response, expected_icps_differ):
    # 确保后端无逻辑错误
    assert response.status_code == 200

    responsedata = json.loads(response.data)

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
@when("客户端发送post请求data_type=1", target_fixture='response')
def response(client, jsondata):
    jsondata["data_type"] = 1
    response = client.post("/connect", json=jsondata)
    return response

@then(parsers.parse("返回错误的料高: {expected_height_load:d}"))
def check_strategy_1_error(app, db, response, expected_height_load):
    # 确保后端无逻辑错误
    assert response.status_code == 200

    responsedata = json.loads(response.data)

    # 确保返回参数符合要求
    actual_height_load = responsedata.get('operating_stations').get('height_load')
    assert expected_height_load == actual_height_load

    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 0

@scenario("./feature/connect.feature", "2.1.1 将任务信息传给时庐获取引导策略")
def test_data_type0():
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
