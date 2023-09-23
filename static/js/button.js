document.getElementById("startBtn").addEventListener("click", function() {
    // 发送请求给后台开始获取数据的函数
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/start");
    xhr.send();
  });
  
  document.getElementById("stopBtn").addEventListener("click", function() {
    // 发送请求给后台停止获取数据的函数
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/stop");
    xhr.send();
  });