import pandas as pd
import datetime
from flask_sqlalchemy import SQLAlchemy
from autoloading.models.sensor import Traffic, loader_num

from autoloading.models.sensor import CoConfig, LoaderConfig

for i in range(loader_num):
    exec(f'from autoloading.models.sensor import Sensor{i+1}')


def test_insert_csvtotraffic(app, db):
    with app.app_context():
        filename = './test/csv/traffic.csv'
        df = pd.read_csv(filename)
        df.to_sql(con=db.engine, name=Traffic.__tablename__, if_exists='append', index=False)
        traffic = db.session.query(Traffic).all()
        assert len(traffic) == 99


def test_insert_csvtodb(app, db):
    with app.app_context():
        filename = './test/csv/sensor4-1-1.csv'
        df = pd.read_csv(filename)

        exec("df.to_sql(con=db.engine, name=Sensor1.__tablename__, if_exists='append', index=False)")
        exec("sensor1 = db.session.query(Sensor1).all()")
        exec("assert len(sensor1) == 10")

def test_db_insert_traffic(app, db):
    with app.app_context():
        traffics = [ Traffic(
            time=datetime.datetime.now(),
            truckid=f'jojo{i}',
            truckload=20.0,
            boxlength=1.0,
            boxwidth=1.0,
            boxheight=1.0,
            truckweightin=10.0,
            truckweightout=20.0,
            goodstype='木片',
            storeid=1,
            loaderid="402A",
            loadcurrent=10.0,
            worktotal=10
        ) for i in range(10)]
        db.session.bulk_save_objects(traffics)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        traffics = Traffic.query.all()
        assert len(traffics) == 10

def test_db_query_traffic(app, db):
    expect_value = 'jojo5'
    actual_value = ''

    with app.app_context():
        traffics = [ Traffic(
            time=datetime.datetime.now(),
            truckid=f'jojo{i}',
            truckload=20.0,
            boxlength=1.0,
            boxwidth=1.0,
            boxheight=1.0,
            truckweightin=10.0,
            truckweightout=20.0,
            goodstype='木片',
            storeid=1,
            loaderid="402A",
            loadcurrent=10.0,
            worktotal=10
        ) for i in range(10)]
        db.session.bulk_save_objects(traffics)
        db.session.commit()
        actual_value = Traffic.query.filter_by(truckid='jojo5').first().truckid

    assert actual_value == expect_value

def test_db_update_loader(app, db):
    expect_value = 20.0 / 10
    actual_value = 0

    with app.app_context():
        co_config1 = CoConfig(
            goods_type='黄豆',
            duration=10,
            weight=20.0,
        )
        co_config2 = CoConfig(
            goods_type='黄豆',
            duration=10,
            weight=30.0,
        )
        loader = LoaderConfig(
            store_id=1,
            loader_id="402A",
        )
        loader.co_config = [co_config1, co_config2]
        db.session.add(loader)
        db.session.commit()

        loader_read = LoaderConfig.query.filter(LoaderConfig.loader_id=="402A").all()[-1]

        actual_value = loader_read.co_config[0].weight / loader_read.co_config[0].duration

    assert actual_value == expect_value

def test_db_update_multiple_loader(app, db):

    with app.app_context():
        co_config = [CoConfig(
            goods_type='黄豆',
            duration=10,
            weight=20.0,
        ) for i in range(10)]
        loader = LoaderConfig(
            store_id=1,
            loader_id=f"402A",
        )
        # loader.co_config = co_config
        for i in range(10):
            loader.co_config.append((CoConfig(
                goods_type='玉米',
                duration=10,
                weight=20.0,
            )))        
        db.session.add(loader)
        db.session.commit()

        loader_read = LoaderConfig.query.filter_by(loader_id="402A").all()
        co_config = loader_read[0].co_config
        print(co_config)

        loader_read = LoaderConfig.query.filter(LoaderConfig.loader_id=="402A").all()[-1]

        co_config_read = CoConfig.query.filter(CoConfig.loader_id==loader_read.id, CoConfig.goods_type=='玉米').all()

        print(co_config_read)
