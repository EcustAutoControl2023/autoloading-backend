import math
import pandas as pd
import json
from pytest_bdd import scenarios, given, when, then, parsers
from autoloading.handlers.loaderpoint import load_point_dict
from autoloading.models.sensor import Traffic

scenarios("feature/loaderpoint.feature")

"""
Background: 初始化实例列表
"""
@given("初始化完成的实例列表", target_fixture="lpdict")
def load_point_dict_created():
    global load_point_dict
    return load_point_dict
"""
END
"""


"""
Scenario: 实例数量测试
"""
@then("长度应该和装料点个数相同(20个)")
def check_length(lpdict):
    assert len(lpdict) == 20
"""
END
"""


"""
重量估计函数测试
"""

@given(parsers.parse("物料类型: {goods_type}"), target_fixture="goods_type")
def goods_type(goods_type):
    # print(f'goods_type: {goods_type}')
    return goods_type

@given(parsers.parse("装料点: {loader_id:d}"), target_fixture="loader_id")
def loader_id(loader_id):
    # print(f'loader_id: {loader_id}')
    return loader_id

@given(parsers.parse("装料用时: {time_difference}"), target_fixture="time_difference", converters={"time_difference": float})
def time_difference(time_difference):
    # print(f'time_difference: {time_difference}')
    return time_difference

@given(parsers.parse("模拟Traffic表数据: {csv_file}"), target_fixture="csv_file")
def csv_file(csv_file):
    # print(f'csv_file: {csv_file}')
    return csv_file

@when("调用对象的weight_estimate方法", target_fixture="estimated_weight")
def call_weight_estimate(app, db, lpdict, goods_type, loader_id, time_difference, csv_file):
    with app.app_context():
        df = pd.read_csv(csv_file)
        df.to_sql(con=db.engine, name=Traffic.__tablename__, if_exists='append', index=False)
        estimated_weight = lpdict.get(loader_id).weight_estimate(goods_type, loader_id, time_difference)

        print(f'\033[31mestimated_weight: {estimated_weight}\033[0m')
        return estimated_weight

@then(parsers.parse("检查估计的重量: {expect_value}"))
def check_estimate_weight(estimated_weight, expect_value):
    expect_value = None if expect_value == "None" else float(expect_value)
    if expect_value is None:
        assert estimated_weight == expect_value
    else:
        assert math.fabs(estimated_weight - expect_value) < 1e-3

"""
END
"""

