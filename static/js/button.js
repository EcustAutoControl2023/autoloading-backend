var socket = io('http://localhost:5000');

var loader_id_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];
var current_loader_id = 1;

var sensor_tablename_list = ['sensor1', 'sensor2', 'sensor3', 'sendor4', 'sensor5', 'sensor6', 'sensor7', 'sensor8', 'sensor9', 'sensor10', 'sensor11', 'sensor12', 'sensor13', 'sensor14', 'sensor15', 'sensor16', 'sensor17', 'sensor18', 'sensor19', 'sensor20'];


var traffic_show_number = 6;

for (var i = 0; i < loader_id_list.length; i++) {
  let loader_id = loader_id_list[i];
  let sensor_tablename = sensor_tablename_list[i];
  let loader_element_id = 'loader_' + loader_id;
  // console.log(`loader_element_id: ${loader_element_id}`);
  let sensor = sensor_tablename;
  let func = genFunction(loader_id, sensor);
  // 使用JQuery绑定点击事件到id为loader_element_id的元素上
  // 当点击该元素时，会调用func函数
  // $('#' + loader_element_id).click(func);
  $(document).ready(function() {
  $('#' + loader_element_id).click(func);
});
}

function genFunction(loader, sensor){
  return () => {
    socket.emit('tab_switch', {'loader': loader, 'sensor': sensor});              
  }
}
