import logging
from flask import Flask
from autoloading.handlers.loaderpoint import LoadPoint, load_point_dict
from autoloading.config import RUNNING
from apscheduler.schedulers.background import BackgroundScheduler
from autoloading.handlers.sensor import read_per_second
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from autoloading.handlers.weight_estimate import weight_estimate
from autoloading.models.sensor import Traffic

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(20)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 20
}
scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)


def sensor(app, loadpoint:LoadPoint):
    
    with app.app_context():
        read_per_second(loadpoint)

def weight():
    weight_estimate()

# def camera(Camera, camera_dict:dict[str, Camera], loaderid:str, jobid:int):
#     global scheduler
#     camera = camera_dict[loaderid]
#     camera.connecting = True

#     # if camera.cap is not None and camera.cap.isOpened():
#     #     camera.cap.release()
#     #     camera.cap = None
#     #     print(f'相机{jobid}已连接,清理！')
#     capture = cv2.VideoCapture(camera.rtsp)
#     # status = camera.connect()

#     if capture.isOpened():
#     # if status:
#         camera.cap = capture
#         camera.cameraStatus = True
        
#         logging.debug(f'相机{jobid}连接成功！')
#         scheduler.remove_job(jobid) # 移除定时任务
#     else:
#         logging.debug(f'相机{jobid}连接失败！')
#         scheduler.remove_job(jobid) # 移除定时任务
    
#     camera.connecting = False

def schedulers_start(app:Flask):
    global RUNNING
    global scheduler

    # 每隔一秒启动一次，同一个进程中不重新添加job和重启
    if RUNNING:
        RUNNING = False
        for key, value in LoadPoint.loader_index_dict.items():
            # FIXME: 检查定时任务是否启动
            logging.debug(f'开始接收装料点{key}的传感器数据！')
            scheduler.add_job(sensor, 'cron', second='*', args=(app, load_point_dict[key]))
        scheduler.add_job(weight, 'cron', hour = '2',minute = '0')
            # scheduler.add_job(sensor, 'date', args=(app, load_point_dict[key]))
    try:
        scheduler.start()
    except Exception as e:
        logging.info(e)
