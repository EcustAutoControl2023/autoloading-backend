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
    let traffic_data_array = Array();
    for (item of traffic_data_queue.toArray())
    {
        // console.log(item)
        traffic_data_array.push(item);
    }
    // 反转数据
    traffic_data_array.reverse();
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
}

traffic_socket.on('traffic_data_queue', function(data) {
    // console.log(data);
    // 遍历数据，添加到表格中
    // 如果数据为空，则不添加
    // console.log(data.length)

    if (data.length == 0) {
        return;
    }
    for (let i = 0; i < data.length; i++) {
        // 将数据添加到队列中
        traffic_data_queue.push(data[i]);
    }
    show_traffic_data();
})


traffic_socket.on('traffic_data', function(data) {
    if (data.modified)
    {
        traffic_data_queue.popRight();
    }
    // 将新的数据添加到队列中
    traffic_data_queue.push(data);
    // console.log(traffic_data_queue);
    show_traffic_data();
});
