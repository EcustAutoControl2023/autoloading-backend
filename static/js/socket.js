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


let url_name = window.location.pathname.split('/')[1];
// index 对应 sensor1, index1 对应 sensor2, 以此类推
let index_table = {
'index': 0, 'index1': 1, 'index2': 2, 'index3': 3, 'index4': 4,
'index5': 5, 'index6': 6, 'index7': 7, 'index8': 8, 'index9': 9,
'index10': 10, 'index11': 11, 'index12': 12, 'index13': 13, 'index14': 14,
'index15': 15, 'index16': 16, 'index17': 17, 'index18': 18, 'index19': 19
};
let index = index_table[url_name];
current_loaderid = loader_id_list[index];

traffic_socket.on('traffic_data_queue', function(data) {
    // 遍历数据，添加到表格中
    // 如果数据为空，则不添加
    // console.log(data[0]["loaderid"]);
    // console.log("current_loaderid: "+current_loaderid);
    if (data.length == 0) {
        return;
    }
    if (data[0]["loaderid"] === current_loaderid)
    {

        if (!traffic_data_queue.isEmpty())
        {
            traffic_data_queue.clear();
        }
        for (let i = 0; i < data.length; i++) {
            // 将数据添加到队列中
            traffic_data_queue.push(data[i]);
        }
        show_traffic_data();

    }

})


traffic_socket.on('traffic_data', function(data) {
    // console.log(data.loaderid);
    // console.log("current_loaderid: "+current_loaderid);
    if (data.loaderid === current_loaderid)
    {
        if (data.modified)
        {
            traffic_data_queue.popRight();
        }
        // 将新的数据添加到队列中
        traffic_data_queue.push(data);
        // console.log(traffic_data_queue);
        show_traffic_data();
    }
});
