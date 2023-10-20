from flask import Flask, request,jsonify  
from flask_sqlalchemy import SQLAlchemy  
from autoloading.models import db
from autoloading.models.sensor import Traffic
import datetime



def update_truck_content(truck_id, update_data):  
    traffic = Traffic.query.filter_by(truck_id=truck_id).last()
    traffic.truck_weight_out = update_data['truck_weight_out']
    db.session.commit()
  

  
#@app.route('/store', methods=['POST'])  
def insert_truck_content(req_time,
                         truck_id,  
                         truck_load,
                         load_current,
                         box_length,
                         box_width,
                         box_height,
                         truck_weight_in,
                         truck_weight_out,
                         goods_type,
                         store_id,
                         loader_id,
                         load_level_height1,
                         load_level_height2,
                         load_time1,
                         load_time2,
                         work_total
                         ):  
    # load_level_height1: 物位计第一次装车高度
    # load_level_height2: 物位计第二次装车高度
    # load_time1: 第一次装车用时
    # load_time2：第二次装车用时
    traffic = Traffic(time = req_time, 
                      truckid=truck_id,
                      truckload = truck_load,
                      boxlength = box_length,
                      boxwidth = box_width,
                      boxheight = box_height,
                      truckweightin = truck_weight_in,
                      truckweightout = truck_weight_out,
                      goodstype = goods_type,
                      storeid = store_id,
                      loaderid = loader_id,
                      loadlevelheight1 = load_level_height1,
                      loadlevelheight2 = load_level_height2,
                      loadtime1 = load_time1,
                      loadtime2 = load_time2,
                      loadcurrent = load_current,
                      worktotal = work_total
)
    db.session.add(traffic)
    db.session.commit()
    from .socket import traffic_data
    traffic_data({
        'truckid': truck_id,
        'truckweightin': truck_weight_in,
        'truckweightout': truck_weight_out,
        'goodstype': goods_type,
        'truckload': truck_load,
        'loadcurrent': load_current,
        'storeid': store_id,
        'loaderid': loader_id,
    })
  

# def query_latest_data_from_database():
#   # 查询数据库中最新的数据
#   data = Traffic.query.all()
#   # 将查询到的数据转换为字典列表
#   data_dict = [{'id': car.id, 'name': car.name, 'price': car.price} for car in data]
#   return data_dict