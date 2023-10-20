var traffic_socket = io('http://localhost:5000');

traffic_socket.on('traffic_data', function() {
    console.log('Connected to server');
});

traffic_socket.on('traffic_data', function(data) {
    // 清空表格
    // $('#car-data').empty();

    // 遍历数据(数据是object，添加到表格中
    console.log(data);
    var row = $('<tr>');
    row.append($('<td style ="color: white" align="center">').text(data['truckid']));
    row.append($('<td style ="color: white" align="center">').text(data['truckweightin']));
    row.append($('<td style ="color: white" align="center">').text(data['truckweightout']));
    row.append($('<td style ="color: white" align="center">').text(data['goodstype']));
    row.append($('<td style ="color: white" align="center">').text(data['truckload']));
    row.append($('<td style ="color: white" align="center">').text(data['loadcurrent']));
    row.append($('<td style ="color: white" align="center">').text(data['storeid']));
    row.append($('<td style ="color: white" align="center">').text(data['loaderid']));
    $('#car-data').append(row);
});