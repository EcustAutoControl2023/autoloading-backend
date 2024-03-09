import logging
import datetime
import cv2
from flask import Flask
from autoloading.handlers.loaderpoint import LoadPoint, load_point_dict
from autoloading.handlers.video import LicensePlateCamera, LoaderCamera, Camera, LOADING_CAMERA, LICENSE_PLATE_CAMERA
from autoloading.config import RUNNING
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def sensor(app, loadpoint:LoadPoint):
    from autoloading.handlers.sensor import read_per_second
    with app.app_context():
        read_per_second(loadpoint)

def camera(Camera, camera_dict:dict[str, Camera], loaderid:str, jobid:str):
    global scheduler
    camera = camera_dict[loaderid]
    capture = cv2.VideoCapture(camera.rtsp)

    if capture.isOpened():
        camera.cap = capture
        logging.debug(f'相机{jobid}连接成功！')
        # 连接成功后，移除定时任务
        scheduler.remove_job(jobid)
    else:
        logging.debug(f'相机{jobid}连接失败！')
        # 延长重连任务时间间隔
        scheduler.reschedule_job(jobid, trigger='interval', seconds=59)
        # scheduler.remove_job(jobid)
    

def schedulers_start(app:Flask):
    global RUNNING
    global scheduler

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
