Feature: connect接口测试
  Scenario Outline: 2.1.1 将任务信息传给时庐获取引导策略
    Given 测试的post文件为: <file>
    And 初始化
    And 三个装料点位: <distance_0>, <distance_1>, <distance_2>
    When 客户端发送post请求data_type=0
    And 手动停止
    And 根据装料点位发送post请求data_type=1
    Then 返回正确的装车策略: <expected_icps_differ>

    Examples: 5种装车过程（最后一种为错误情况）
    | file                        | distance_0 | distance_1 | distance_2 | expected_icps_differ |
    | ./test/json/postdata-1.json | 1.1        | 1.1        | 1.1        | [1.1]                |
    | ./test/json/postdata-1.json | 1.2        | 1.2        | 1.1        | [1.2, 1.1]           |
    | ./test/json/postdata-1.json | 1.1        | 1.2        | 1.2        | [1.1, 1.2]           |
    | ./test/json/postdata-1.json | 1.1        | 1.2        | 1.3        | [1.1, 1.2, 1.3]      |
    # | ./test/json/postdata-1.json | 1.2        | 1.1        | 1.2        | []                   |

  Scenario Outline: 2.1.1 将任务信息传给时庐获取引导策略——异常测试(data_type=1未收到结束或移动点位响应，但请求data_type=0)
    Given 测试的post文件为: <file>
    And 三个装料点位: <distance_0>, <distance_1>, <distance_2>
    When 客户端发送post请求data_type=0
    And 客户端发送post请求data_type=0
    Then 返回错误的装车策略: <expected_icps_differ>

    Examples: 5种装车过程（最后一种为错误情况）
    | file                        | distance_0 | distance_1 | distance_2 | expected_icps_differ |
    | ./test/json/postdata-1.json | 1.1        | 1.1        | 1.1        | [1.1]                |

  Scenario Outline: 2.1.2 集卡引导到位，获取时庐的 PLC 控制策略
    Given 测试的post文件为: <file>
    And 三个装料点位: <distance_0>, <distance_1>, <distance_2>
    And 模拟的装车数据: <csv_file>
    When 客户端发送post请求data_type=0
    And 创建生成器: 模拟客户端发送post请求data_type=1
    Then 使用生成器模拟请求，返回正确的装车策略直至装车停止: <expected_return_file>

    Examples: 
      | file                        | distance_0 | distance_1 | distance_2 | csv_file              | expected_return_file |
      | ./test/json/postdata-1.json | 1.1        | 1.1        | 1.1        | ./csv/sensor4-1-1.csv | ./test/ret/ret1.json |
      | ./test/json/postdata-2.json | 1.1        | 1.1        | 1.1        | ./csv/sensor4-1-1.csv | ./test/ret/ret2.json |
      | ./test/json/postdata-1.json | 1.1        | 1.2        | 1.2        | ./csv/sensor4-1-2.csv | ./test/ret/ret3.json |
      | ./test/json/postdata-1.json | 1.1        | 1.2        | 1.3        | ./csv/sensor4-1-3.csv | ./test/ret/ret4.json |
    # | ./test/json/postdata-1.json | 1.2        | 1.1        | 1.2        | ./csv/sensor4-1-2.csv | ./test/ret/ret5.json |

  Scenario Outline: 2.1.2 集卡引导到位，获取时庐的 PLC 控制策略——异常测试(未请求data_type=0)
    Given 测试的post文件为: <file>
    And 三个装料点位: <distance_0>, <distance_1>, <distance_2>
    When 客户端发送post请求data_type=1
    Then 返回错误的料高: <expected_height_load>

    Examples: 
      | file                        | distance_0 | distance_1 | distance_2 | csv_file              | expected_height_load |
      | ./test/json/postdata-1.json | 1.1        | 1.1        | 1.1        | ./csv/sensor4-1-1.csv | -1                   |

  Scenario Outline: 2.1.3 装车完成后，获取出闸重量
    Given 测试的post文件为: <file>
    And 初始化
    And 三个装料点位: <distance_0>, <distance_1>, <distance_2>
    And 模拟出闸量队列: <weight_out_list>
    When 客户端发送post请求data_type=0
    And 手动停止
    And 根据装料点位发送post请求data_type=1
    And 出闸
    And 客户端发送post请求data_type=2
    Then 返回正确的出闸重量: <expected_weight_out>

    Examples: 5种装车过程（最后一种为错误情况）
    | file                        | distance_0 | distance_1 | distance_2 | weight_out_list | expected_weight_out |
    | ./test/json/postdata-1.json | 1.1        | 1.1        | 1.1        | [20]            | 20                  |
    | ./test/json/postdata-1.json | 1.2        | 1.2        | 1.1        | [20]            | 20                  |
    | ./test/json/postdata-1.json | 1.1        | 1.2        | 1.2        | [20]            | 20                  |
    | ./test/json/postdata-1.json | 1.1        | 1.2        | 1.3        | [20]            | 20                  |

  Scenario Outline: 2.1.3 两辆车装车完成后，合作方提供第一辆的出闸重量
    Given 测试的post文件为: <file>
    And 初始化
    And 三个装料点位: <distance_0>, <distance_1>, <distance_2>
    And 车辆队列: <plate_list>
    And 模拟出闸量队列: <weight_out_list>
    When 车牌变更
    And 客户端发送post请求data_type=0
    And 手动停止
    And 根据装料点位发送post请求data_type=1
    And 车牌变更
    And 手动停止
    And 根据装料点位发送post请求data_type=1
    And 车牌变更
    And 出闸
    And 客户端发送post请求data_type=2
    Then 返回正确的出闸重量: <expected_weight_out>

    Examples: 5种装车过程（最后一种为错误情况）
    | file                        | distance_0 | distance_1 | distance_2 | plate_list            | weight_out_list | expected_weight_out |
    | ./test/json/postdata-1.json | 1.1        | 1.1        | 1.1        | ["A86", "A87", "A86"] | [20]            | 20                  |
    | ./test/json/postdata-1.json | 1.1        | 1.2        | 1.2        | ["A86", "A87", "A86"] | [20]            | 20                  |
    | ./test/json/postdata-1.json | 1.1        | 1.1        | 1.1        | ["A86", "B38", "A86"] | [20]            | 20                  |
