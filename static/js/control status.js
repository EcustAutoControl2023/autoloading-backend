var socket = io('http://localhost:5000');
var controlstatusElement = document.getElementById('control status');  // 获取显示状态的元素，可以根据实际情况修改id或选择器  
  
socket.on('control_status', function(data) {  // 处理接收到的状态更新事件  
    controlstatusElement.innerHTML = data === 1 ? '控制器状态：运行中' : '控制器状态：未运行';  // 根据状态值更新显示文字  
});  


var load_socket = io('http://localhost:5000');
var loadstatusElement = document.getElementById('loading status');  // 获取显示状态的元素，可以根据实际情况修改id或选择器  
  
load_socket.on('loading_status', function(data) {  // 处理接收到的状态更新事件  
    loadstatusElement.innerHTML = data === 0 ? '装车状态：正在装车' : '装车状态：未装车';  // 根据状态值更新显示文字  
});  
