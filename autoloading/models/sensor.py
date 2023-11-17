import logging
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

    @staticmethod
    def before_insert(target,value,initiator):
        logging.debug('trigger before insert')
        database_capacity = Traffic.query.order_by(Traffic.id.desc()).count()
        logging.debug('database_capacity is %s',database_capacity) 
        # 数据库容量大于10,000条时，删除最早的一条数据
        if database_capacity >= 100000:
            logging.debug('database is full')
            # 删除最早的一条数据
            traffic = Traffic.query.order_by(Traffic.id.asc()).first()
            db.session.delete(traffic)
            # db.session.commit()

# 添加监听器
# db.event.listen(Traffic, 'before_insert',Traffic.before_insert)

    




