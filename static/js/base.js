$(function () {

    //echart_3交通就业人员
    function echart_3() {
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
                data:['铁路运输业'],
                textStyle:{
                    color: '#fff'
                },
                top: '4%'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            toolbox: {
                orient: 'vertical',
                right: '1%',
                top: '2%',
                iconStyle: {
                    color: '#FFEA51',
                    borderColor: '#FFA74D',
                    borderWidth: 1,
                },
                feature: {
                    saveAsImage: {},
                    magicType: {
                        show: true,
                        type: ['line','bar','stack','tiled']
                    }
                }
            },
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
                name: '人',
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
            color: ['#FF4949','#FFA74D','#FFEA51','#4BF0FF','#44AFF0','#4E82FF','#584BFF','#BE4DFF','#F845F1'],
            series: [
                {
                    name:'铁路运输业',
                    type:'line',
                    data:[57197, 51533, 57000, 58150, 55748]
                },
                {
                    name:'公路运输业',
                    type:'line',
                    data:[148054, 150198, 144943, 138157, 114234]
                },
                {
                    name:'水上运输业',
                    type:'line',
                    data:[27100, 25568, 25734, 24393, 23851]
                },
                {
                    name:'航空运输业',
                    type:'line',
                    data:[1795, 3306, 4151, 5538, 4766]
                },
                {
                    name:'管道运输业',
                    type:'line',
                    data:[1586,567,647,1235,1186]
                },
                {
                    name:'装卸搬运和其他运输服务业',
                    type:'line',
                    data:[4448, 11742, 12706, 10666, 10902]
                }
            ]
        };
        myChart.setOption(option);
    }
});
