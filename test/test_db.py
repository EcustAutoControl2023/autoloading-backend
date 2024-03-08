import pandas as pd
import datetime
from autoloading.models.sensor import Traffic, loader_num

for i in range(loader_num):
    exec(f'from autoloading.models.sensor import Sensor{i+1}')


def test_insert_csvtotraffic(app, db):
    with app.app_context():
        filename = './test/csv/traffic.csv'
        df = pd.read_csv(filename)
        df.to_sql(con=db.engine, name=Traffic.__tablename__, if_exists='append', index=False)
        traffic = db.session.query(Traffic).all()
        assert len(traffic) == 12


def test_insert_csvtodb(app, db):
    with app.app_context():
        filename = './test/csv/sensor4-1-1.csv'
        df = pd.read_csv(filename)
        df.to_sql(con=db.engine, name=Sensor1.__tablename__, if_exists='append', index=False)
        sensor1 = db.session.query(Sensor1).all()
        assert len(sensor1) == 10

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

