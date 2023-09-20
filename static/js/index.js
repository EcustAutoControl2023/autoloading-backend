$(function () {
    echart_3();

    //echart_3货物周转量
    function echart_3() {
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart_3'));
        myChart.clear();
        option = {
            title: {
                text: ''
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data:['物位计数据'],
                textStyle:{
                    color: '#fff'
                },
                top: '8%'
            },
            grid: {
                top: '15%',
                left: '5%',
                right: '5%',
                bottom: '30%',
                containLabel: true
            },
            color: ['#FF4949'],
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: ['1s','2s','3s','4s','5s'],
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
                    name:'物料高度',
                    type:'line',
                    data:[1, 2, 3, 4, 3]
                }
            ]
        };
        myChart.setOption(option);
    }

    //点击跳转
    // $('.t_btn7').click(function(){
    //     window.location.href = "./page/index.html?id=7";
    // });
});
