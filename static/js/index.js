class Queue {
    constructor(len=5) {
      this.items = [];
      this.len = len - 1;
    }
  
    // 将队列内容转换为数组
    toArray() {
      return this.items;
    }
  
    // 入队
    push(element) {
      if (this.items.length > this.len)
      {
          this.items.pop();
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
  
    // 判断队列是否为空
    isEmpty() {
      return this.items.length === 0;
    }
  }
  
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
              data:['物位计数据(mm)'],
              textStyle:{
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
              name:'近1分钟数据',
              type: 'category',
              boundaryGap: false,
              data: ['1','2','3','4','5','6','7','8','9','10',
                      '11','12','13','14','15','16','17','18','19','20',
                      '21','22','23','24','25','26','27','28','29','30',
                      '31','32','33','34','35','36','37','38','39','40',
                      '41','42','43','44','45','46','47','48','49','50',
                      '51','52','53','54','55','56','57','58','59','60'],
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
                  data: data_queue.toArray()
              }
          ],
          animation: false
      };
      myChart.setOption(option);
  }
  
  var sensor_socket = io('http://localhost:5000');
  
  const show_num = 60;
  var data_queue = new Queue(show_num);
  
  sensor_socket.on('sensor_data', (data)=>{
      data_queue.push(data.value);
      console.log(data_queue.toArray())
      echart_3();
  });
  
  
  $(function () {
      echart_3();
  
  
      //点击跳转
      // $('.t_btn7').click(function(){
      //     window.location.href = "./page/index.html?id=7";
      // });
  });
  