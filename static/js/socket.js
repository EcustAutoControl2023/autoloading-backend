var traffic_socket = io('http://localhost:5000');

traffic_socket.on('traffic_data', function() {
    console.log('Connected to server');
});

let traffic_show_num = 6;
var traffic_data_queue = new Queue(traffic_show_num);

function show_traffic_data() {
    // 清空表格
    $('#car-data').empty();
    // 遍历数据，添加到表格中
    traffic_data_array = traffic_data_queue.toArray()
    // 反转数据
    traffic_data_array.reverse()
    for (let i = 0; i < traffic_data_queue.len; i++) {
        var row = $('<tr>');
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].truckid));
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].truckweightin));
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].truckweightout));
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].goodstype));
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].truckload));
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].loadcurrent));
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].storeid));
        row.append($('<td  style ="color: white" align="center">').text(traffic_data_array[i].loaderid));
        $('#car-data').append(row);
    }
    traffic_data_array.reverse()
}

traffic_socket.on('traffic_data_queue', function(data) {
    // console.log(data);
    // 遍历数据，添加到表格中
    for (let i = 0; i < data.length; i++) {
        // 将数据添加到队列中
        traffic_data_queue.push(data[i]);
    }
    show_traffic_data();
})


traffic_socket.on('traffic_data', function(data) {
    // 将新的数据添加到队列中
    traffic_data_queue.push(data);
    // console.log(traffic_data_queue);
    show_traffic_data();
});