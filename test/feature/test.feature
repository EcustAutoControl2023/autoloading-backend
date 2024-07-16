Feature: 测试程序
  Scenario Outline: 一次装料，记录时间
    Given 测试的post文件为: <file>
    And 初始化
    And 三个装料点位: <distance_0>, <distance_1>, <distance_2>
    And 等待<time>秒
    And 装车量: <load_current>
    When 客户端发送post请求data_type=0
    # 记录开始时间
    And 根据装料点位发送post请求data_type=1
    And 延迟发送
    And 手动停止
    # 记录结束时间
    And 根据装料点位发送post请求data_type=1
    Then 返回正确的装车时间: <expected_duration>

    Examples: 四种装车情况
    | file                  | distance_0 | distance_1 | distance_2 | time | load_current | expected_duration |
    | ./test/json/test.json | 1.1        | 1.1        | 1.1        | 1    | 50.5          | 1                 |
    | ./test/json/test.json | 1.1        | 1.1        | 1.2        | 1    | 50.5          | 2                 |
    | ./test/json/test.json | 1.1        | 1.2        | 1.2        | 1    | 50.5          | 2                 |
    | ./test/json/test.json | 1.1        | 1.2        | 1.3        | 1    | 50.5          | 3                 |

