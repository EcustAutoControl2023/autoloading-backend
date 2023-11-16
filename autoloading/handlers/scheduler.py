import logging
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from flask import Flask
from autoloading.handlers.loaderpoint import LoadPoint

def sensor(app, Sensor, loader_id):
    from autoloading.handlers.sensor import read_per_second, sread_per_second
    with app.app_context():
        # logging.debug(f'开始接收装料点{loader_id}的传感器数据！')
        # read_per_second()
        # logging.debug(f'Sensor is {Sensor}')
        sread_per_second(Sensor)

def schedulers_start(app:Flask):
    # 只启动一次，并且是后台任务
    scheduler = BackgroundScheduler()
    # for key, value in LoadPoint.loader_index_dict.items():
    #     logging.debug(f'SensorList[{value}] is {LoadPoint.SensorList[value]}')
    #     scheduler.add_job(sensor, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=value), args=(app, LoadPoint.SensorList[value], key))
    # 每隔一秒启动一次
    for key, value in LoadPoint.loader_index_dict.items():
        logging.debug(f'开始接收装料点{key}的传感器数据！')
        scheduler.add_job(sensor, 'interval', seconds=1, args=(app, LoadPoint.SensorList[value], key))

    scheduler.start()