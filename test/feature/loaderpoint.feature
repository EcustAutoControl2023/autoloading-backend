Feature: 测试LoaderPoint类
  Background: 初始化实例列表
    Given 初始化完成的实例列表

  Scenario: 实例数量测试
    Then 长度应该和装料点个数相同(20个)

  Scenario Outline: 重量估计函数测试
    Given 物料类型: <goods_type>
    And 装料点: <loader_id>
    And 装料用时: <time_difference>
    And 模拟Traffic表数据: <csv_file>

    When 调用对象的weight_estimate方法

    Then 检查估计的重量: <expect_value>

    Examples:
      | goods_type | loader_id | time_difference | csv_file                 | expect_value |
      | 油菜籽     | 401A      | 2.              | ./test/csv/traffic.csv   | 0.096        |
    # | 油菜籽     | 402B      | 2.              | ./test/csv/traffic-2.csv | None         |
    # | 油菜籽     | 402B      | 2.              | ./test/csv/traffic-2.csv | None         |

