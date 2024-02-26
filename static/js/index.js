class Queue {
    constructor(len = 5) {
        this.items = [];
        this.len = len - 1;
    }

    clear() {
        this.items = [];
    }

    // 将队列内容转换为数组
    toArray() {
        return this.items.copyWithin(0, this.len + 1);
    }

    // 入队
    push(element) {
        if (this.items.length > this.len) {
            this.pop();
        }
        this.items.push(element);
    }

    // 出队
    pop() {
        if (this.isEmpty()) {
            return "Queue is empty";
        }
        return this.items.shift();
    }

    popRight() {
        if (this.isEmpty()) {
            return "Queue is empty";
        }
        return this.items.pop();
    }

    // 判断队列是否为空
    isEmpty() {
        return this.items.length === 0;
    }
}

let tablename = '';
const sensor_show_num = 60;
let data_queue = new Queue(sensor_show_num);
let data_queue1 = new Queue(sensor_show_num);

function echart_3(chartid, data_queue) {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById(chartid));
    myChart.clear();
    option = {
        title: {
            text: ''
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['物位计数据(mm)'],
            textStyle: {
                color: '#fff'
            },
            top: '8%'
        },
        grid: {
            top: '10%',
            left: '3%',
            right: '20%',
            bottom: '5%',
            containLabel: true
        },
        color: ['#FF4949'],
        xAxis: {
            name: '近1分钟数据',
            type: 'category',
            boundaryGap: false,
            data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
                '31', '32', '33', '34', '35', '36', '37', '38', '39', '40',
                '41', '42', '43', '44', '45', '46', '47', '48', '49', '50',
                '51', '52', '53', '54', '55', '56', '57', '58', '59', '60'],
            splitLine: {
                show: false
            },
            axisLine: {
                lineStyle: {
                    color: '#fff'
                }
            }
        },
        yAxis: {
            name: '物料高度',
            type: 'value',
            splitLine: {
                show: false
            },
            axisLine: {
                lineStyle: {
                    color: '#fff'
                }
            }
        },
        series: [
            {
                name: '物料高度',
                type: 'line',
                data: data_queue.toArray()
            }
        ],
        animation: false
    };
    myChart.setOption(option);
}

var sensor_socket = io('http://localhost:5000');


sensor_socket.on('sensor_data', (data) => {
    // console.log("tablename out: " + data.tablename);
    if (data.tablename === tablename) {
        // console.log("tablename: " + data.tablename);
        // console.log("data: " + data.value);
        data_queue.push(data.value);
        echart_3('chart_3', data_queue);
    }
    //   console.log(data_queue.toArray())
});


$(function () {
    echart_3('chart_3', data_queue);
    let url_name = window.location.pathname.split('/')[1];
    //console.log(url_name);

    let loader_id_list = [
        "401A", "402A", "403A",
        "401B", "402B", "403B",
        "501A", "502A", "503A",
        "501B", "502B", "503B",
        "601A", "602A", "603A", "604A",
        "601B", "602B", "603B", "604B",
    ];

    let sensor_tablename_list = ['sensor1', 'sensor2', 'sensor3', 'sensor4', 'sensor5', 'sensor6', 'sensor7', 'sensor8', 'sensor9', 'sensor10', 'sensor11', 'sensor12', 'sensor13', 'sensor14', 'sensor15', 'sensor16', 'sensor17', 'sensor18', 'sensor19', 'sensor20'];

    // index 对应 sensor1, index1 对应 sensor2, 以此类推
    let index_table = {
        'index1': 0, 'index2': 1, 'index3': 2, 'index4': 3,
        'index5': 4, 'index6': 5, 'index7': 6, 'index8': 7, 'index9': 8,
        'index10': 9, 'index11': 10, 'index12': 11, 'index13': 12, 'index14': 13,
        'index15': 14, 'index16': 15, 'index17': 16, 'index18': 17, 'index19': 18, 'index20': 19
    };
    let index = index_table[url_name];
    tablename = sensor_tablename_list[index];
    sensor_socket.emit('traffic_data_request', {number: traffic_show_number, loaderid: loader_id_list[index]});
    socket.emit('tab_switch', {'loader': loader_id_list[index], 'sensor': sensor_tablename_list[index]});
    //点击跳转
    // $('.t_btn7').click(function(){
    //     window.location.href = "./page/index.html?id=7";
    // });
});

