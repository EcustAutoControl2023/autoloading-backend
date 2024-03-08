import logging
from flask import Flask
from autoloading.handlers.loaderpoint import LoadPoint, load_point_dict
from autoloading.config import RUNNING
from apscheduler.schedulers.background import BackgroundScheduler

def sensor(app, loadpoint:LoadPoint):
    from autoloading.handlers.sensor import read_per_second
    with app.app_context():
        read_per_second(loadpoint)

def schedulers_start(app:Flask):
    global RUNNING
    scheduler = BackgroundScheduler()

    # 每隔一秒启动一次，同一个进程中不重新添加job和重启
    if RUNNING:
        RUNNING = False
        for key, value in LoadPoint.loader_index_dict.items():
            # FIXME: 检查定时任务是否启动
            logging.debug(f'开始接收装料点{key}的传感器数据！')
            scheduler.add_job(sensor, 'interval', seconds=1, args=(app, load_point_dict[key]))
    try:
        scheduler.start()
    except Exception as e:
        logging.info(e)
