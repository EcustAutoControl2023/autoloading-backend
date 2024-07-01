Feature: connect接口测试(模拟装车模式)
  Scenario Outline: 5.1.1 1、集卡引导到位，获取时庐的PLC控制策略
    Given 测试的post文件: <file>
    And 初始化post数据
    And 装料点位: <distance_list>
    And 模拟的装车数据: <csv_file>
    When 模拟装车模式
    Then 模拟请求，正常装车: <expected_icps_differ_list>
    Examples:
      | file                        | distance_list   | csv_file             | expected_icps_differ_list                |
      | ./test/json/postdata-1.json | [1.1, 1.1, 1.1] | ./csv/sensor14-2.csv | [[1.1], []]                              |
      | ./test/json/postdata-1.json | [1.2, 1.2, 1.1] | ./csv/sensor14-2.csv | [[1.2, 1.1], [1.1], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.2] | ./csv/sensor14-2.csv | [[1.1, 1.2], [1.2], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.3] | ./csv/sensor14-2.csv | [[1.1, 1.2, 1.3], [1.2, 1.3], [1.3], []] |
