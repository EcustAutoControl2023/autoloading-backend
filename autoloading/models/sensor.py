from .base import db


# 初始化数据表及属性
class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer)
    # 时间戳
    time = db.Column(db.DateTime)



class Traffic(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    truckid = db.Column(db.Integer)
    #boxlength = db.Column(db.Integer)
    #boxwidth = db.Column(db.Integer)
    #boxheight = db.Column(db.Integer)
    #distance0 = db.Column(db.Integer)
    #distance1 = db.Column(db.Integer)
    #distance2 = db.Column(db.Integer)
    truckload = db.Column(db.Integer)
    loadcurrent = db.Column(db.Integer)
    truckweightin = db.Column(db.Integer)
    truckweightout = db.Column(db.Integer)
    goodstype = db.Column(db.Integer)
    storeid = db.Column(db.Integer)
    loaderid = db.Column(db.Integer)


    




