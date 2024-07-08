var socket = io('http://localhost:5000');

function show_truck_id_confirm(data)
{
    let show = $("#dialog").css("display");
    let dialog = document.getElementById("dialog");
    let img_url = data["img_url"];
    dialog.innerHTML = ` \
    <div id="dialog" style="display: block;">\
                        <div class="contents">\
                            <div class="aclose">\
                                <span>车牌OCR勘误</span>\
                                <div class="close">\
                                    <a class="a" href="javascript:close_confirm();"></a>\
                                </div>\
                                <div class="img_container">\
                                    <img src=${img_url}>\
                                </div>\
                            </div>\
                            <div class="btn_container">\
                                <button class="btn" onclick="truck_id_confirm_message()">允许作业</button>\
                            </div>\
                        </div>\
                    </div>\
`;
    $("#dialog").css("display", show=="none"?"block":"none");
}

function show_center_confirm(data)
{
    let show = $("#dialog").css("display");
    let dialog = document.getElementById("dialog");
    let img_url = data["img_url"];
    dialog.innerHTML = ` \
    <div id="dialog" style="display: block;">\
                        <div class="contents">\
                            <div class="aclose">\
                                <span>现场确认</span>\
                                <div class="close">\
                                    <a class="a" href="javascript:close_confirm();"></a>\
                                </div>\
                                <div class="img_container">\
                                    <img src=${img_url}>\
                                </div>\
                            </div>\
                            <div class="btn_container">\
                                <button class="btn" onclick="center_confirm_message()">允许作业</button>\
                            </div>\
                        </div>\
                    </div>\
`;
    $("#dialog").css("display", show=="none"?"block":"none");
}

function close_confirm()
{
    let show = $("#dialog_confirm").css("display");
    $("#dialog").css("display", show=="none"?"block":"none");
}

socket.on('connect',()=>{
  console.log('connected!');
})

socket.on('truck_id_popup', function(data) {
    show_truck_id_confirm(data);
});

socket.on('center_popup', function(data) {
    show_center_confirm(data);
});

function truck_id_confirm_message()
{
    socket.emit('truck_id_popup_confirm', {data: true})
    close_confirm();
}

function center_confirm_message()
{
    socket.emit('center_popup_confirm', {data: true})
    close_confirm();
}

function show_confirm()
{
    let show = $("#dialog").css("display");
    let dialog = document.getElementById("dialog");
    dialog.innerHTML = ' <div class="contents">\
                            <div class="aclose">\
                                <span>现场确认</span>\
                                <div class="close">\
                                    <a class="a" href="javascript:close_confirm();"></a>\
                                </div>\
                                <div class="img_container">\
                                <img src="https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png">\
                                </div>\
                                </div>\
                                <div class="btn_container">\
                                <input type="submit" class="submit-btn" value="允许作业" >\
                                </div>\
                            </div>\
                        </div>\
';
    $("#dialog").css("display", show=="none"?"block":"none");
}



function show()
{
    let show = $("#dialog").css("display");
    let dialog = document.getElementById("dialog");
    dialog.innerHTML = ' <div class="contents">\
                                <div class="aclose">\
                                    <span>测量信息录入</span>\
                                    <div class="close">\
                                        <a class="a" href="javascript:close();"></a>\
                                    </div>\
                                </div>\
                                <div class="contains">\
                                    <div class="aform">\
\
                                    <div class="form">\
                                        <form method="post" action="/store" style="line-height: 2;">\
                                            <table>\
                                                <tr>\
                                                    <td>\
                                                        <label class="form-label" for="name">车辆最大载重(t):</label>\
                                                    </td>\
                                                    <td>\
                                                        <label class="form-label" for="name"></label>本次装载量(t):</label>\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td>\
                                                        <input type="text" name="maxload" class="white-text">              \
                                                    </td>\
                                                    <td>\
                                                        <input type="text" name="load" class="white-text">\
                                                    </td>\
\
                                                </tr>\
                                                <tr>\
                                                    <td>\
                                                        <label class="form-label" for="name">进场车辆重量(t):</label>\
                                                    </td>\
                                                    <td>\
                                                        <label class="form-label" for="name">出场车辆重量(t):</label>\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td>\
                                                        <input type="text" name="inweight" class="white-text">              \
                                                    </td>\
                                                    <td>\
                                                        <input type="text" name="outweight" class="white-text">\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td>\
                                                        <label class="form-label" for="name">装货仓库编号：</label>   \
                                                    </td>\
                                                    <td>\
                                                        <label class="form-label" for="name">装料机编号：</label>\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td>\
                                                        <input type="text" name="warehousenumber">                 \
                                                    </td>\
                                                    <td>\
                                                        <input type="text" name="machine number">\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td>\
                                                        <span style=color:white>货物类别：</span>\
                                                    </td>\
                                                    <td>\
                                                        <select name="category" class="select">\
                                                        <option value="material" class="select">原材料</option>\
                                                        <option value="food" class="select">食物</option>\
                                                        <option value="equipment" class="select">器具</option>\
                                                        <option value="furniture" class="select">家具</option>\
                                                        </select>\
                                                    </td>\
                                                </tr>\
                                                <tr >\
                                                    <td colspan="2">\
                                                        <label for="licenseplate" style=color:white style="line-height: 2;">车牌识别正确：</label>\
                                                    <input type="checkbox" id="licenseplate">\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td colspan="2">\
                                                        <label for="vehiclealignment" style=color:white style="line-height: 2;">车辆偏移物料口：</label>\
                                                        <input type="checkbox" id="vehiclealignment">\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td colspan="2">\
                                                        <label for="allowoperation" style=color:white style="line-height: 2;">允许作业：</label>\
                                                        <input type="checkbox" id="allowoperation">\
                                                    </td>\
                                                </tr>\
                                                <tr>\
                                                    <td colspan="2">\
                                                        <input type="submit" class="submit-btn" value="提交" >\
                                                    </td>\
                                                </tr>\
                                            </table>\
                                            </form>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>\
    ';
    $("#dialog").css("display", show=="none"?"block":"none");
}
function close()
{
    let show = $("#dialog").css("display");
    $("#dialog").css("display", show=="none"?"block":"none");
}
