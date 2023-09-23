from .base import db


# 初始化数据表及属性
class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer)
    # 时间戳
    time = db.Column(db.DateTime)