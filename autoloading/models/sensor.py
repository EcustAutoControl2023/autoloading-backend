import logging
from .base import db

# 装料口数量
loader_num = 20

# 初始化数据表及属性
class SensorBase(db.Model):
    '''
    SensorDB
    '''
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer)
    # 时间戳
    time = db.Column(db.DateTime)
    tablename = db.Column(db.String(10), nullable=True)

    @staticmethod
    def before_insert(target,value,initiator):
        database_capacity = type(initiator).query.order_by(type(initiator).id.desc()).count()
        # 数据库容量大于10,000条时，删除最早的一条数据
        if database_capacity >= 100000:
            # 删除最早的一条数据
            ids_to_delete = type(initiator).query.order_by(type(initiator).id.desc()).offset(10).all()
            for id in ids_to_delete:
                db.session.delete(id)
            # db.session.commit()

# 使用SensorBase创建20个数据表Sensor类（Sensor1~Sensor20)，用db.create_all()创建20个数据表
def create_sensor_table_class():
    for i in range(1, loader_num+1):
        class_name = 'Sensor' + str(i)
        sensor_class = type(class_name, (SensorBase,), {
            '__tablename__': 'sensor' + str(i)
            })
        globals()[sensor_class.__name__] = sensor_class
        # 添加trigger
        # exec(f'db.event.listen({sensor_class.__name__}, "before_insert",{sensor_class.__name__}.before_insert)')

create_sensor_table_class()

class Traffic(db.Model):
    '''
    TrafficDB
    '''

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(20), nullable=False)
    truckid = db.Column(db.String(20), nullable=False)
    truckload = db.Column(db.Float, nullable=False)
    boxlength = db.Column(db.Float, nullable=False)
    boxwidth = db.Column(db.Float, nullable=False)
    boxheight = db.Column(db.Float, nullable=False)
    truckweightin = db.Column(db.Float, nullable=True)
    truckweightout = db.Column(db.Float, nullable=False)
    goodstype = db.Column(db.String(10), nullable=False)
    storeid = db.Column(db.Integer, nullable=False)
    loaderid = db.Column(db.String(20), nullable=True)
    loadlevelheight1 = db.Column(db.Integer, nullable=True)
    loadlevelheight2 = db.Column(db.Integer, nullable=True)
    loadlevelheight3 = db.Column(db.Integer, nullable=True)
    loadstarttime = db.Column(db.DateTime, nullable=True)
    loadendtime = db.Column(db.DateTime, nullable=True)
    loadtimetotal = db.Column(db.Integer, nullable=True)
    loadcurrent = db.Column(db.Float, nullable=True)
    loadestimate = db.Column(db.Float, nullable=True)
    worktotal = db.Column(db.Integer, nullable=False)
    jobid = db.Column(db.String(20), nullable=True)
    loadstatus = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(20), nullable=True)
    stackpos = db.Column(db.String(20), nullable=True)
    loadheight = db.Column(db.Float, nullable=True)
    loadpoint1 = db.Column(db.Float, nullable=True)
    loadpoint2 = db.Column(db.Float, nullable=True)
    loadpoint3 = db.Column(db.Float, nullable=True)
    type_of_opening = db.Column(db.String(20), nullable=True)
    opening_length_bias = db.Column(db.Float, nullable=True)
    opening_width_bias = db.Column(db.Float, nullable=True)
    opening_length = db.Column(db.Float, nullable=True)
    opening_width = db.Column(db.Float, nullable=True)

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

