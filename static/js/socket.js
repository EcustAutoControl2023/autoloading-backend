let traffic_socket = io('http://localhost:5000');

traffic_socket.on('traffic_data', function() {
    console.log('Connected to server');
});

let traffic_show_num = 6;
var traffic_data_queue = new Queue(traffic_show_num);

let overview_show_num = 20;
var overview_data_queue = new Queue(overview_show_num);

function show_table_data(id, data_queue) {
    // 清空表格
    $(id).empty();
    // 遍历数据，添加到表格中
    let data_array = Array();
    for (item of data_queue.toArray())
    {
        // console.log(item)
        data_array.push(item);
    }
    // 反转数据
    data_array.reverse();
    for (let i = 0; i < data_array.length; i++) {
        var row = $('<tr>');
        for (let data in data_array[i])
        {
            if (data === 'modified')
                continue;
            row.append($('<td  style ="color: white" align="center">').text(data_array[i][data]));
        }
        $(id).append(row);
    }
}


let url_name = window.location.pathname.split('/')[1];
// index1 对应 sensor1, index1 对应 sensor2, 以此类推
let index_table = {
        'index1': 0, 'index2': 1, 'index3': 2, 'index4': 3,
        'index5': 4, 'index6': 5, 'index7': 6, 'index8': 7, 'index9': 8,
        'index10': 9, 'index11': 10, 'index12': 11, 'index13': 12, 'index14': 13,
        'index15': 14, 'index16': 15, 'index17': 16, 'index18': 17, 'index19': 18, 'index20': 19
    };
let index = index_table[url_name];
let loaderid_list = [
    "401A", "402A", "403A",
    "401B", "402B", "403B",
    "501A", "502A", "503A",
    "501B", "502B", "503B",
    "601A", "602A", "603A", "604A",
    "601B", "602B", "603B", "604B",
];
current_loaderid = loaderid_list[index];
console.log('current_loaderid: '+current_loaderid);

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

        // if (!traffic_data_queue.isEmpty())
        // {
        //     traffic_data_queue.clear();
        // }
        for (let i = 0; i < data.length; i++) {
            // 将数据添加到队列中
            traffic_data_queue.push(data[i]);
        }
        show_table_data('#car-data', traffic_data_queue);

    }

})


traffic_socket.on('traffic_data', function(data) {
    console.log(data.loaderid);
    console.log("current_loaderid: "+current_loaderid);
    if (data.loaderid === current_loaderid)
    {
        if (data.modified)
        {
            // traffic_data_queue.popRight();
            traffic_data_queue.updateElem(
                ["truckid", data.truckid],
                data
            )
        }
        else{
            // 将新的数据添加到队列中
            traffic_data_queue.push(data);
        }
        // console.log(traffic_data_queue);
        show_table_data('#car-data', traffic_data_queue);
    }
});

function get_overview_data(data)
{
    // 遍历数据，添加到表格中
    // 如果数据为空，则不添加
    console.log(data);
    if (data.length == 0) {
        return;
    }
    if (!overview_data_queue.isEmpty())
    {
        overview_data_queue.clear();
    }
    for (let i = data.length; i > 0; i--) {
        // 将数据添加到队列中
        overview_data_queue.push(data[i-1]);
    }
    console.log(overview_data_queue.len);
    show_table_data('#overview-data', overview_data_queue);

}

traffic_socket.on('overview_data_queue', get_overview_data);

traffic_socket.on('overview_data', get_overview_data);


