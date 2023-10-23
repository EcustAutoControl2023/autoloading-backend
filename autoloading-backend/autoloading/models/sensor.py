from .base import db


# 初始化数据表及属性
class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer)
    # 时间戳
    time = db.Column(db.DateTime)



class Traffic(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(20), nullable=False)
    truckid = db.Column(db.String(20), nullable=False)
    truckload = db.Column(db.Float, nullable=False)
    boxlength = db.Column(db.Float, nullable=False)
    boxwidth = db.Column(db.Float, nullable=False)
    boxheight = db.Column(db.Float, nullable=False)
    truckweightin = db.Column(db.Float, nullable=False)
    truckweightout = db.Column(db.Float, nullable=False)
    goodstype = db.Column(db.String(10), nullable=False)
    storeid = db.Column(db.Integer, nullable=False)
    loaderid = db.Column(db.Integer, nullable=False)
    loadlevelheight1 = db.Column(db.Integer, nullable=True)
    loadlevelheight2 = db.Column(db.Integer, nullable=True)
    loadtime1 = db.Column(db.DateTime, nullable=True)
    loadtime2 = db.Column(db.DateTime, nullable=True)
    loadcurrent = db.Column(db.Float, nullable=False)
    worktotal = db.Column(db.Integer, nullable=False)


    




