import logging
from flask import Response
import cv2
from queue import Queue
import os
from abc import ABC, abstractmethod

import threading, time

from autoloading.handlers.loaderpoint import LoadPoint


# 摄像头类
class Camera(ABC):
    def __init__(self, rtsp) -> None:
        self.rtsp = rtsp
        self.cap  = None
        self.loaderid = None
        self.frame_alt = open(os.getcwd() + '/static/img/video_alt.png', 'rb').read()

    def ishealthy(self):
        if self.cap is None:
            return False
        return True

    def connect(self):
        '''
        没用到
        '''
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.rtsp)
            if self.cap.isOpened():
                return True
            self.cap.release()
        self.cap = None
        return False
        # from autoloading.config import CAP_TIME_OUT
        # capture = None
        #
        # time_out = CAP_TIME_OUT
        # start = time.time()
        # cap_thread = videocapture_Thread(self.rtsp)
        # cap_thread.daemon = True
        # cap_thread.start()
        # cap_thread.join(timeout=time_out)
        # logging.debug(f'摄像头链接超时时间:{time.time() - start}')
        # capture = cap_thread.result
        # logging.debug(f'capture：{capture}')
        # if capture is not None:
        #     self.cap = capture
        #     self.flag.put(1)
        #     return True
        # return False

    def say(self):
        return f"rtsp: {self.rtsp}"

    @classmethod
    def empty_frame(cls):
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'+ b'\r\n')

    @abstractmethod
    def scheduler(self):
        '''
        子类实现，对应的定时任务
        '''
        pass

    def show_frame(self):

        while True:
            try:
                (self.status, self.frame) = self.cap.read()
                if self.status is not True:
                    self.scheduler() # 断线重连
                    frame = self.frame_alt
                else:
                    ret, buffer = cv2.imencode('.jpg', self.frame)
                    frame = buffer.tobytes()
            except Exception as e:
                frame = self.frame_alt # 显示加载失败图片
                time.sleep(0.5) # 防止卡死

            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

class LoaderCamera(Camera):
    loader_video_url_list = [
        "rtsp://admin:1234567a@172.16.175.58:554/h265/ch1/sub/av_stream",#url_1 401南监控相机
        "rtsp://admin:1234567a@172.16.175.64:554/h265/ch1/sub/av_stream",#url_2 402南监控相机
        "rtsp://admin:1234567a@172.16.175.70:554/h265/ch1/sub/av_stream",#url_3 403南监控相机
        "rtsp://admin:1234567a@172.16.175.76:554/h265/ch1/sub/av_stream",#url_4 401北监控相机
        "rtsp://admin:1234567a@172.16.175.82:554/h265/ch1/sub/av_stream",#url_5 402北监控相机
        "rtsp://admin:1234567a@172.16.175.88:554/h265/ch1/sub/av_stream",#url_6 403北监控相机
        "rtsp://admin:1234567a@172.16.175.94:554/h265/ch1/sub/av_stream",#url_7 501南监控相机
        "rtsp://admin:1234567a@172.16.175.100:554/h265/ch1/sub/av_stream",#url_8 502南监控相机
        "rtsp://admin:1234567a@172.16.175.106:554/h265/ch1/sub/av_stream",#url_9 503南监控相机
        "rtsp://admin:1234567a@172.16.175.112:554/h265/ch1/sub/av_stream",#url_10 501北监控相机
        "rtsp://admin:1234567a@172.16.175.118:554/h265/ch1/sub/av_stream",#url_11 502北监控相机
        "rtsp://admin:1234567a@172.16.175.124:554/h265/ch1/sub/av_stream",#url_12 503北监控相机
        "rtsp://admin:1234567a@172.16.175.130:554/h265/ch1/sub/av_stream",#url_13 601南监控相机
        "rtsp://admin:1234567a@172.16.175.136:554/h265/ch1/sub/av_stream",#url_14 602南监控相机
        "rtsp://admin:1234567a@172.16.175.142:554/h265/ch1/sub/av_stream",#url_15 603南监控相机
        "rtsp://admin:1234567a@172.16.175.148:554/h265/ch1/sub/av_stream",#url_16 604南监控相机
        "rtsp://admin:1234567a@172.16.175.154:554/h265/ch1/sub/av_stream",#url_17 601北监控相机
        "rtsp://admin:1234567a@172.16.175.160:554/h265/ch1/sub/av_stream",#url_18 602北监控相机
        "rtsp://admin:1234567a@172.16.175.166:554/h265/ch1/sub/av_stream",#url_19 603北监控相机
        "rtsp://admin:1234567a@172.16.175.172:554/h265/ch1/sub/av_stream",#url_20 604北监控相机    
    ]

    def __init__(self, loaderid:str) -> None:
        rtsp = self.loader_video_url_list[LoadPoint.loader_index_dict[loaderid]]
        super().__init__(rtsp)
        self.loaderid = loaderid
        self.scheduler()

    def scheduler(self):
        from autoloading.handlers.scheduler import scheduler, camera
        logging.debug(f'开始连接装料点{self.loaderid}的料口相机数据！')
        id = f'loadercamera: {self.loaderid}'
        scheduler.add_job(camera, 'interval', seconds=1, args=(LoaderCamera, LOADING_CAMERA, self.loaderid, id), id=id)

class LicensePlateCamera(Camera):
    license_video_url_list = [
        "rtsp://admin:1234567a@172.16.175.61:554/h265/ch1/sub/av_stream",#url_1 401南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.67:554/h265/ch1/sub/av_stream",#url_2 402南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.73:554/h265/ch1/sub/av_stream",#url_3 403南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.79:554/h265/ch1/sub/av_stream",#url_4 401北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.85:554/h265/ch1/sub/av_stream",#url_5 402北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.91:554/h265/ch1/sub/av_stream",#url_6 403北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.97:554/h265/ch1/sub/av_stream",#url_7 501南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.103:554/h265/ch1/sub/av_stream",#url_8 502南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.109:554/h265/ch1/sub/av_stream",#url_9 503南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.115:554/h265/ch1/sub/av_stream",#url_10 501北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.121:554/h265/ch1/sub/av_stream",#url_11 502北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.127:554/h265/ch1/sub/av_stream",#url_12 503北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.133:554/h265/ch1/sub/av_stream",#url_13 601南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.139:554/h265/ch1/sub/av_stream",#url_14 602南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.145:554/h265/ch1/sub/av_stream",#url_15 603南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.151:554/h265/ch1/sub/av_stream",#url_16 604南车牌识别相机
        "rtsp://admin:1234567a@172.16.175.157:554/h265/ch1/sub/av_stream",#url_17 601北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.163:554/h265/ch1/sub/av_stream",#url_18 602北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.169:554/h265/ch1/sub/av_stream",#url_19 603北车牌识别相机
        "rtsp://admin:1234567a@172.16.175.175:554/h265/ch1/sub/av_stream",#url_20 604北车牌识别相机    
    ]

    def __init__(self, loaderid:str) -> None:
        rtsp = self.license_video_url_list[LoadPoint.loader_index_dict[loaderid]]
        super().__init__(rtsp)    
        self.loaderid = loaderid    
        self.scheduler()

    def scheduler(self):
        from autoloading.handlers.scheduler import scheduler, camera
        logging.debug(f'开始连接装料点{self.loaderid}的车牌相机数据！')
        id = f'licenseplatecamera: {self.loaderid}'
        scheduler.add_job(camera, 'interval', seconds=1, args=(LicensePlateCamera, LICENSE_PLATE_CAMERA, self.loaderid, id), id=id)

# 装料口摄像头dict
LOADING_CAMERA:dict[str, Camera] = dict()

# 车牌摄像头dict
LICENSE_PLATE_CAMERA:dict[str, Camera] = dict()

def gen_video_feed(loaderid:str):
    def video_feed():
        camera = None
        try:
            camera = LOADING_CAMERA[loaderid]
        except KeyError:
            LOADING_CAMERA[loaderid] = LoaderCamera(loaderid)
            camera = LOADING_CAMERA[loaderid]
        return Response(camera.show_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return video_feed

def gen_license_video_feed(loaderid:str):
    def video_feed():
        camera = None
        try:
            camera = LICENSE_PLATE_CAMERA[loaderid]
        except KeyError:
            LICENSE_PLATE_CAMERA[loaderid] = LicensePlateCamera(loaderid)
            camera = LICENSE_PLATE_CAMERA[loaderid]
        return Response(camera.show_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    return video_feed


# # 减少摄像头连接不上超时等待问题
# class videocapture_Thread(threading.Thread):
#     def __init__(self, rtsp):
#         super(videocapture_Thread, self).__init__()
#         self.result = None
#         self.rtsp = rtsp
#
#     def run(self):
#         self.result = self.open_videocapture()
#
#     def open_videocapture(self):
#         cap = cv2.VideoCapture(self.rtsp)
#         if cap.isOpened():
#             return cap
#         else:
#             cap.release()
#             return None
#
