from flask import Flask, request  
from flask_sqlalchemy import SQLAlchemy  
from autoloading.models import db
from autoloading.models.sensor import Traffic
import datetime
  
#@app.route('/store', methods=['POST'])  
def insert_truck_content(req_time,truck_load,truck_id,load_current,truck_weight_in,truck_weight_out,goods_type,store_id,loader_id):  
    # current_time = datetime.datetime.now()
    # truck_load = request.form['maxload']  
    # load_current = request.form['load']
    # truck_weight_in = request.form['inweight']    
    # truck_weight_out = request.form['outweight']
    # goods_type = request.form['category']
    # store_id = request.form['warehousenumber']  
    # loader_id = request.form['machine number']  
    # information = Traffic(time = current_time,
    #                       truckload = truck_load,loadcurrent = load_current,
    #                       truckweightin = truck_weight_in,truckweightout = truck_weight_out,
    #                       goodstype = goods_type,storeid = store_id,loaderid = loader_id,
    #                       )  
    # db.session.add(information)  
    # db.session.commit()  
    # return "内容已存储到数据库"  
    traffic = Traffic(     time = req_time, truckid=truck_id,
                           truckload = truck_load, loadcurrent = load_current,
                           truckweightin = truck_weight_in, truckweightout = truck_weight_out,
                           goodstype = goods_type, storeid = store_id, loaderid = loader_id,
)
    db.session.add(traffic)
    db.session.commit()
  
