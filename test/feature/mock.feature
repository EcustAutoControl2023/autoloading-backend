Feature: connect接口测试(模拟装车模式)
  Scenario Outline: 5.1.1 1、集卡引导到位，获取时庐的PLC控制策略
    Given 测试的post文件: <file>
    And 初始化post数据
    And 装料点位: <distance_list>
    And 模拟的装车数据: <csv_file>
    And 装车量: <load_current>
    When 模拟装车模式
    Then 模拟请求，正常装车: <expected_icps_differ_list>
    Examples:
      | file                        | distance_list   | csv_file             | load_current | expected_icps_differ_list                |
      | ./test/json/postdata-1.json | [1.1, 1.1, 1.1] | ./csv/sensor14-2.csv | 5.5          | [[1.1], []]                              |
      | ./test/json/postdata-1.json | [1.2, 1.2, 1.1] | ./csv/sensor14-2.csv | 5.5          | [[1.2, 1.1], [1.1], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.2] | ./csv/sensor14-2.csv | 5.5          | [[1.1, 1.2], [1.2], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.3] | ./csv/sensor14-2.csv | 5.5          | [[1.1, 1.2, 1.3], [1.2, 1.3], [1.3], []] |
  Scenario Outline: 5.1.3 2、反馈出闸信息
    Given 测试的post文件: <file>
    And 初始化post数据
    And 装料点位: <distance_list>
    And 模拟的装车数据: <csv_file>
    And 车牌号: <plate_list>
    And 出闸数据: <weightout_list>
    And 装车量: <load_current>
    When 模拟装车模式
    Then 模拟请求，正常装车(车队): <expected_icps_differ_list>
    Examples:
      | file                        | distance_list   | csv_file             | plate_list    | weightout_list | load_current | expected_icps_differ_list                |
      | ./test/json/postdata-1.json | [1.1, 1.1, 1.1] | ./csv/sensor14-2.csv | ['闽1','闽2'] | [-1, 40]       | 0.05         | [[1.1], []]                              |
      | ./test/json/postdata-1.json | [1.2, 1.2, 1.1] | ./csv/sensor14-2.csv | ['闽1','闽2'] | [-1, 40]       | 0.05         | [[1.2, 1.1], [1.1], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.2] | ./csv/sensor14-2.csv | ['闽1','闽2'] | [-1, 40]       | 0.05         | [[1.1, 1.2], [1.2], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.3] | ./csv/sensor14-2.csv | ['闽1','闽2'] | [-1, 40]       | 0.05         | [[1.1, 1.2, 1.3], [1.2, 1.3], [1.3], []] |
  Scenario Outline: 5.1.1 1、集卡引导到位，获取时庐的PLC控制策略，第一次装料物料就满了直接结束
    Given 测试的post文件: <file>
    And 初始化post数据
    And 装料点位: <distance_list>
    And 模拟的装车数据: <csv_file>
    And 装车量: <load_current>
    When 模拟装车模式
    Then 模拟请求，正常装车: <expected_icps_differ_list>
    Examples:
      | file                        | distance_list   | csv_file             | load_current | expected_icps_differ_list     |
      | ./test/json/postdata-1.json | [1.1, 1.1, 1.1] | ./csv/sensor14-2.csv | 0.0          | [[1.1], []]                   |
      | ./test/json/postdata-1.json | [1.2, 1.2, 1.1] | ./csv/sensor14-2.csv | 0.0          | [[1.2, 1.1], [], []]          |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.2] | ./csv/sensor14-2.csv | 0.0          | [[1.1, 1.2], [], []]          |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.3] | ./csv/sensor14-2.csv | 0.0          | [[1.1, 1.2, 1.3], [], [], []] |
  # Scenario Outline: 5.1.1 1、集卡引导到位，获取时庐的PLC控制策略，重量估计测试
  #   Given 测试的post文件: <file>
  #   And 初始化post数据
  #   And 装料点位: <distance_list>
  #   And 模拟的装车数据: <csv_file>
  #   And 装车量: <load_current>
  #   When 模拟装车模式
  #   Then 模拟请求，正常装车: <expected_icps_differ_list>
  #   Examples:
  #     | file                        | distance_list   | csv_file             | load_current | expected_icps_differ_list     |
  #     | ./test/json/postdata-1.json | [1.1, 1.1, 1.1] | ./csv/sensor14-3.csv | 28.3         | [[1.1], []]                   |
  #     | ./test/json/postdata-1.json | [1.2, 1.2, 1.1] | ./csv/sensor14-3.csv | 28.3         | [[1.2, 1.1], [], []]          |
  #     | ./test/json/postdata-1.json | [1.1, 1.2, 1.2] | ./csv/sensor14-3.csv | 28.3         | [[1.1, 1.2], [], []]          |
  #     | ./test/json/postdata-1.json | [1.1, 1.2, 1.3] | ./csv/sensor14-3.csv | 28.3         | [[1.1, 1.2, 1.3], [], [], []] |
