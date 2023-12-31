import logging
from .base import db

loader_num = 3
# 初始化数据表及属性
class SensorBase(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer)
    # 时间戳
    time = db.Column(db.DateTime)

    @staticmethod
    def before_insert(target,value,initiator):
        # logging.debug('trigger before insert')
        # logging.debug(f'target is {target}')
        # logging.debug(f'value is {value}')
        # logging.debug(f'initiator is {initiator}')
        database_capacity = type(initiator).query.order_by(type(initiator).id.desc()).count()
        # logging.debug('database_capacity is %s',database_capacity) 
        # 数据库容量大于10,000条时，删除最早的一条数据
        if database_capacity >= 10:
            # logging.debug('database is full')
            # 删除最早的一条数据
            sensor = type(initiator).query.order_by(type(initiator).id.asc()).first()
            db.session.delete(sensor)
            # db.session.commit()

# 使用SensorBase创建20个数据表Sensor类（Sensor1~Sensor20)，并且可以用db.create_all()创建20个数据表
def create_sensor_table_class():
    for i in range(1, loader_num+1):
        class_name = 'Sensor' + str(i)
        sensor_class = type(class_name, (SensorBase,), {
            # 重写before_insert方法
            '__tablename__': 'sensor' + str(i)
            })
        globals()[sensor_class.__name__] = sensor_class
        # 添加监听器
        exec(f'db.event.listen({sensor_class.__name__}, "before_insert",{sensor_class.__name__}.before_insert)')


create_sensor_table_class()

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
        if database_capacity >= 10000:
            logging.debug('database is full')
            # 删除最早的一条数据
            traffic = Traffic.query.order_by(Traffic.id.asc()).first()
            db.session.delete(traffic)
            # db.session.commit()

# 添加监听器
# db.event.listen(Traffic, 'before_insert',Traffic.before_insert)

    




