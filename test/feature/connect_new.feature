Feature: connect接口测试
  Scenario Outline: 5.1.1 0、推送任务信息，返回引导策略
    Given 测试的post文件: <file>
    And 初始化post数据
    And 装料点位: <distance_list>
    When 手动停止模式
    Then 测试异常终止
    And 测试装车策略（手动停止）: <expected_icps_differ_list>

    Examples: 5种装车过程（最后一种为错误情况）
      | file                        | distance_list   | expected_icps_differ_list                |
      | ./test/json/postdata-1.json | [1.1, 1.1, 1.1] | [[1.1], []]                              |
      | ./test/json/postdata-1.json | [1.2, 1.2, 1.1] | [[1.2, 1.1], [1.1], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.2] | [[1.1, 1.2], [1.2], []]                  |
      | ./test/json/postdata-1.json | [1.1, 1.2, 1.3] | [[1.1, 1.2, 1.3], [1.2, 1.3], [1.3], []] |
      | ./test/json/postdata-1.json | []              | []                                       |

