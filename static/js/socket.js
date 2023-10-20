var traffic_socket = io('http://localhost:5000');

traffic_socket.on('traffic_data', function() {
    console.log('Connected to server');
});

traffic_socket.on('traffic_data', function(data) {
    // 清空表格
    // $('#car-data').empty();

    // 遍历数据，添加到表格中
    for (var i = 0; i < data.length; i++) {
        var row = $('<tr>');
        row.append($('<td>').text(data[i].truckid));
        row.append($('<td>').text(data[i].truckweightin));
        row.append($('<td>').text(data[i].truckweightout));
        row.append($('<td>').text(data[i].goodstype));
        row.append($('<td>').text(data[i].truckload));
        row.append($('<td>').text(data[i].loadcurrent));
        row.append($('<td>').text(data[i].storeid));
        row.append($('<td>').text(data[i].loaderid));
        $('#car-data').append(row);
    }
});