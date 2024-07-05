import ast
import datetime
import time
import json
from pytest_bdd import scenarios, given, when, then, parsers
from autoloading.handlers.loaderpoint import LoadPoint
from autoloading.models.sensor import Traffic
from .conftest import printr, udp_client
from .test_common import *

scenarios("feature/connect_new.feature")

@then(parsers.parse("测试装车策略（手动停止）: {expected_icps_differ_list}"), converters={"expected_icps_differ_list": ast.literal_eval})
def check_strategy_manualstop(app, client, db, expected_icps_differ_list:list, postdata, distance_list):
    printr(expected_icps_differ_list, "expected_icps_differ_list")
    
    ea_zip = zip(distance_list, expected_icps_differ_list)

    # 第一次请求装车策略
    postdata['data_type'] = 0
    postdata['operating_stations']['icps_differ_current'] = 1.1
    postdata['operating_stations']['temp_manual_stop'] = 0
    response0 = client.post("/connect", json=postdata)
    check_response(response0, 0)

    # 第三辆车
    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 3

    for distance, expected_icps_differ in ea_zip:
        printr(distance, "distance")
        printr(expected_icps_differ, "expected_icps_differ")
        printr(postdata, "postdata")

        # 点位移动
        postdata['data_type'] = 1
        postdata['operating_stations']['icps_differ_current'] = distance
        response1 = client.post("/connect", json=postdata)
        check_response(response1, 1)

        # 再次请求装车策略
        postdata['data_type'] = 0
        response0 = client.post("/connect", json=postdata)
        printr(response0.json, "data_type0 response")
        check_response(response0, 0)
        actual_icps_differ = response0.json.get('operating_stations').get('icps_differ')
        actual_icps_differ = [actual_icps_differ] if type(actual_icps_differ) is not list else actual_icps_differ
        assert response0.json.get('operating_stations').get('icps_differ') == expected_icps_differ

    # 装车完成（手动停止）
    postdata["data_type"] = 3
    postdata["operating_stations"]["auto_select"] = False
    response3 = client.post("/connect", json=postdata)
    check_response(response3, 3)
    # postdata['data_type'] = 1
    # postdata['operating_stations']['temp_manual_stop'] = 1
    # response1 = client.post("/connect", json=postdata)
    # assert response1.json.get('operating_stations').get('work_finish') == 1
    # check_response(response1, 1)

    # 点位移动
    postdata['data_type'] = 1
    postdata['operating_stations']['temp_manual_stop'] = 0
    response1 = client.post("/connect", json=postdata)
    check_response(response1, 1)

    # 完成时再次请求装车策略
    postdata['data_type'] = 0
    # postdata['operating_stations']['icps_differ_current'] = None
    response0 = client.post("/connect", json=postdata)
    check_response(response0, 0)
    printr(response0.json, "response0: final")
    assert response0.json.get('operating_stations').get('icps_differ') == []
    assert response0.json.get('operating_stations').get('work_finish') == 1

@then("测试异常终止")
def check_strategy_exception(app, client, db, postdata, distance_list):
    # 第一次请求装车策略
    postdata['data_type'] = 0
    postdata['operating_stations']['icps_differ_current'] = 1.1
    postdata['operating_stations']['temp_manual_stop'] = 0
    response0 = client.post("/connect", json=postdata)
    check_response(response0, 0)

    # 第一辆车
    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 1

    # 点位移动
    postdata['data_type'] = 1
    postdata['operating_stations']['icps_differ_current'] = distance_list[0] if len(distance_list) > 0 else None
    response1 = client.post("/connect", json=postdata)
    check_response(response1, 1)

    # 异常终止
    # postdata['data_type'] = 1
    # postdata['operating_stations']['temp_manual_stop'] = 1
    # response1 = client.post("/connect", json=postdata)
    # assert response1.json.get('operating_stations').get('work_finish') == (0 if len(distance_list) > 1 else 1)
    # check_response(response1, 1)
    postdata["data_type"] = 3
    postdata["operating_stations"]["auto_select"] = False
    response3 = client.post("/connect", json=postdata)
    check_response(response3, 3)

    # 完成时再次请求装车策略
    postdata['data_type'] = 0
    postdata['operating_stations']['icps_differ_current'] = None
    ori_truck_id = postdata['operating_stations']['truck_id']
    postdata['operating_stations']['truck_id'] = 'test'
    response0 = client.post("/connect", json=postdata)
    check_response(response0, 0)
    postdata['operating_stations']['truck_id'] = ori_truck_id

    # 第二辆车
    with app.app_context():
        traffics = db.session.query(Traffic).all()
        assert len(traffics) == 2
