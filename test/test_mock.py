import ast
import time
from pytest_bdd import then, parsers, scenarios
from autoloading.handlers.loaderpoint import SensorData
from autoloading.models.sensor import Traffic

from .conftest import printr
from .test_common import *
exec(f'from autoloading.models.sensor import Sensor13')
exec(f'from autoloading.models.sensor import Sensor14')

scenarios("feature/mock.feature")

@then(parsers.parse("模拟请求，正常装车: {expected_icps_differ_list}"), converters={"expected_icps_differ_list": ast.literal_eval})
def check_strategy_1_normal(app, db, client, postdata, gen_post, mock_resume, distance_list, expected_icps_differ_list):
    # 等待数据库中有传感器数据（新数据库最开始没有数据）
    printr(expected_icps_differ_list, "expected_icps_differ_list")
    
    ea_list = list(zip(distance_list, expected_icps_differ_list))
    ea_index = 0

    sleep(1.1)

    for _ in range(5):
        postdata["data_type"] = 0
        response0 = client.post("/connect", json=postdata)
        printr(response0.json, "response0 -> data_type=0")
        check_response(response0, 0)
        actual_icps_differ = response0.json.get('operating_stations').get('icps_differ')
        actual_icps_differ = [actual_icps_differ] if type(actual_icps_differ) is not list else actual_icps_differ
        assert actual_icps_differ == ea_list[ea_index][1]
        assert response0.json.get('operating_stations').get('work_finish') == 0

    postdata["data_type"] = 1
    postdata['operating_stations']['icps_differ_current'] = ea_list[ea_index][0]

    responsedata = dict()

    mock_resume(postdata)

    for response in gen_post:
        with app.app_context():
            traffics = db.session.query(Traffic).all()
            assert len(traffics) == 1

        responsedata = check_response(response, 1)

        # 点位移动测试
        if responsedata.get('operating_stations').get('allow_plc_work') == 0 and \
            responsedata.get('operating_stations').get('work_finish') != 1:
            ea_index += 1
            if ea_index >= len(ea_list):
                break
            postdata["data_type"] = 0
            response0 = client.post("/connect", json=postdata)
            printr(response0.json, "response0 -> data_type=0")
            check_response(response0, 0)
            postdata["data_type"] = 1
            postdata['operating_stations']['icps_differ_current'] = ea_list[ea_index][0]
            actual_icps_differ = response0.json.get('operating_stations').get('icps_differ')
            actual_icps_differ = [actual_icps_differ] if type(actual_icps_differ) is not list else actual_icps_differ
            assert response0.json.get('operating_stations').get('icps_differ') == ea_list[ea_index][1]

        # 装车完成测试
        if responsedata.get('operating_stations').get('work_finish') == 1:
            # 完成时再次请求装车策略
            postdata['data_type'] = 0
            # postdata['operating_stations']['icps_differ_current'] = None
            response0 = client.post("/connect", json=postdata)
            check_response(response0, 0)
            printr(response0.json, "response final -> data_type=0")
            assert response0.json.get('operating_stations').get('icps_differ') == []

            with app.app_context():
                traffics = db.session.query(Traffic).all()
                assert len(traffics) == 1

        # # 假设客户端每隔1s请求一次装车策略
        sleep(1)

@then(parsers.parse("模拟请求，正常装车(车队): {expected_icps_differ_list}"), converters={"expected_icps_differ_list": ast.literal_eval})
def check_strategy_1_normal_carlist(app, db, client, postdata, gen_post, mock_resume, distance_list, plate_list, weightout_list, expected_icps_differ_list):
    # 等待数据库中有传感器数据（新数据库最开始没有数据）
    printr(expected_icps_differ_list, "expected_icps_differ_list")
    
    ea_list = list(zip(distance_list, expected_icps_differ_list))

    pw_list = zip(plate_list, weightout_list)

    sleep(1.1)

    for plate, weightout in pw_list:

        ea_index = 0

        postdata["data_type"] = 0
        postdata['operating_stations']['truck_id'] = plate
        response0 = client.post("/connect", json=postdata)
        printr(response0.json, "response0 -> data_type=0")
        check_response(response0, 0)
        actual_icps_differ = response0.json.get('operating_stations').get('icps_differ')
        actual_icps_differ = [actual_icps_differ] if type(actual_icps_differ) is not list else actual_icps_differ
        assert actual_icps_differ == ea_list[ea_index][1]

        if weightout != -1:
            postdata["data_type"] = 2
            postdata['operating_stations']['truck_id'] = plate_list[0]
            postdata['operating_stations']['truck_weight_out'] = weightout
            response2 = client.post("/connect", json=postdata)
            printr(response2.json, "response0 -> data_type=2")
            check_response(response2, 2)
            assert response2.json.get('operating_stations').get('truck_id') == plate_list[0]
            postdata["operating_stations"]["truck_id"] = plate
            with app.app_context():
                traffics = db.session.query(Traffic).all()
                assert len(traffics) == 2
                last_traffic = db.session.query(Traffic).filter_by(truckid=plate_list[0]).first()
                assert last_traffic != None
                assert last_traffic.truckweightout != None
                assert last_traffic.truckweightout == weightout

        postdata["data_type"] = 1
        postdata['operating_stations']['icps_differ_current'] = ea_list[ea_index][0]

        responsedata = dict()

        mock_resume(postdata)
        for response in gen_post:
            with app.app_context():
                traffics = db.session.query(Traffic).all()
                assert len(traffics) == 1

            responsedata = check_response(response, 1)

            if responsedata.get('operating_stations').get('allow_plc_work') == 0 and \
                responsedata.get('operating_stations').get('work_finish') != 1:
                ea_index += 1
                if ea_index >= len(ea_list):
                    break
                postdata["data_type"] = 0
                response0 = client.post("/connect", json=postdata)
                printr(response0.json, "response0 -> data_type=0")
                check_response(response0, 0)
                postdata["data_type"] = 1
                postdata['operating_stations']['icps_differ_current'] = ea_list[ea_index][0]
                actual_icps_differ = response0.json.get('operating_stations').get('icps_differ')
                actual_icps_differ = [actual_icps_differ] if type(actual_icps_differ) is not list else actual_icps_differ
                assert response0.json.get('operating_stations').get('icps_differ') == ea_list[ea_index][1]

            if responsedata.get('operating_stations').get('work_finish') == 1:
                # 完成时再次请求装车策略
                postdata['data_type'] = 0
                # postdata['operating_stations']['icps_differ_current'] = None
                response0 = client.post("/connect", json=postdata)
                check_response(response0, 0)
                printr(response0.json, "response final -> data_type=0")
                assert response0.json.get('operating_stations').get('icps_differ') == []
                assert response0.json.get('operating_stations').get('work_finish') == 1

                with app.app_context():
                    traffics = db.session.query(Traffic).all()
                    assert len(traffics) == 1

        # # 假设客户端每隔1s请求一次装车策略
        # time.sleep(1)

@then(parsers.parse("模拟请求，重量测试: {expected_weight_list}"), converters={"expected_weight_list": ast.literal_eval})
def check_strategy_1_normal_weight_estimate(app, db, client, postdata, gen_post, mock_resume, distance_list, expected_weight_list):
    # 等待数据库中有传感器数据（新数据库最开始没有数据）
    printr(expected_weight_list, "expected_weight_list")
    
    sleep(1.1)

    icps_index = 0

    for _ in range(5):
        postdata["data_type"] = 0
        response0 = client.post("/connect", json=postdata)
        printr(response0.json, "response0 -> data_type=0")
        check_response(response0, 0)
        actual_icps_differ = response0.json.get('operating_stations').get('icps_differ')
        actual_icps_differ = [actual_icps_differ] if type(actual_icps_differ) is not list else actual_icps_differ
        assert response0.json.get('operating_stations').get('work_finish') == 0

    postdata["data_type"] = 1
    postdata['operating_stations']['icps_differ_current'] = distance_list[icps_index]

    responsedata = dict()
    weight_estimate_new = 0
    weight_estimate_old = 0

    mock_resume(postdata)
    for response in gen_post:
        with app.app_context():
            traffics = db.session.query(Traffic).all()
            assert len(traffics) == 1

        responsedata = check_response(response, 1)

        # 点位移动测试
        if responsedata.get('operating_stations').get('allow_plc_work') == 0 and \
            responsedata.get('operating_stations').get('work_finish') != 1:
            while True:
                with app.app_context():
                    load_height = SensorData(-1)
                    if responsedata.get('operating_stations').get('loader_id') == "601A":
                        load_height = db.session.query(Sensor13).all()[-1]
                    elif responsedata.get('operating_stations').get('loader_id') == "602A":
                        load_height = db.session.query(Sensor14).all()[-1]
                    printr(load_height.data, "sensor")
                    if load_height.data < 3.4:
                        break
                    else:
                        time.sleep(1)
            icps_index += 1
            if icps_index >= len(distance_list):
                break
            postdata["data_type"] = 0
            response0 = client.post("/connect", json=postdata)
            printr(response0.json, "response0 -> data_type=0")
            check_response(response0, 0)
            postdata["data_type"] = 1
            postdata['operating_stations']['icps_differ_current'] = distance_list[icps_index]

        # 打印重量测试
        weight_estimate_new = responsedata.get('operating_stations').get('work_weight_reality')
        printr(weight_estimate_new, "weight_estimate")
        assert weight_estimate_new >= weight_estimate_old

        # 装车完成测试
        if responsedata.get('operating_stations').get('work_finish') == 1:
            # 完成时再次请求装车策略
            postdata['data_type'] = 0
            # postdata['operating_stations']['icps_differ_current'] = None
            response0 = client.post("/connect", json=postdata)
            check_response(response0, 0)
            printr(response0.json, "response final -> data_type=0")
            assert response0.json.get('operating_stations').get('icps_differ') == []

            with app.app_context():
                traffics = db.session.query(Traffic).all()
                assert len(traffics) == 1

        # # 假设客户端每隔1s请求一次装车策略
        sleep(1)
