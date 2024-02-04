let overview_socket = io('http://localhost:5000');
let overview_show_number = 20

$(function () {
    overview_socket.emit('overview_data_request', {number: overview_show_number});
    // overview_socket.emit('overview_data_request', {number: overview_show_number});
    // let url_name = window.location.pathname.split('/')[1];
    //点击跳转
    // $('.t_btn7').click(function(){
    //     window.location.href = "./page/index.html?id=7";
    // });
});


