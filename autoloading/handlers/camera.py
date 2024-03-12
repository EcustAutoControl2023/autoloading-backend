import os, time, logging
from queue import Queue
from abc import ABC, abstractmethod
import cv2


# 摄像头类
class Camera(ABC):
    def __init__(self, rtsp) -> None:
        self.rtsp = rtsp
        self.cap  = None
        self.index = None
        self.jobid = None
        self.cameraStatus = False
        self.frame_alt = open(os.getcwd() + '/static/img/valt.png', 'rb').read()
        self.frame_queue = Queue(maxsize=2)

    def ishealthy(self):
        if self.cap is None:
            return False
        return True

    def run(self):
        while True:
            try:
                # (self.status, self.frame) = self.cap.read()
                if self.cap.grab():
                    (self.status, self.frame) = self.cap.retrieve()
                else:
                    self.status = False
                if self.status is not True:
                    logging.debug(f'摄像头{self.jobid}断线！')
                    self.scheduler()
                    self.frame_queue.put(self.frame_alt)
                else:
                    ret, buffer = cv2.imencode('.jpg', self.frame)
                    frame = buffer.tobytes()
                    self.frame_queue.put(frame)
                    # logging.debug(f'摄像头{self.jobid}显示！')
            except Exception as e:
                if self.cap is not None:
                    logging.debug(f'摄像头{self.jobid}寄了！')
                    self.cap.release()
                self.frame_queue.put(self.frame_alt)


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

        logging.debug(f'摄像头{self.jobid}开始显示！')
        start = time.time()
        while True:
            from autoloading.config import CAP_TIME_OUT
            if (time.time() - start) > CAP_TIME_OUT and self.cameraStatus is False:
                logging.debug(f'摄像头{self.__class__}{self.jobid}显示超时！')
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n'+ b'\r\n')
                break

            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + self.frame_queue.get() + b'\r\n')

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

    def __init__(self, index:int) -> None:
        rtsp = self.loader_video_url_list[index]
        super().__init__(rtsp)
        self.index = index
        self.start()

    def start(self):
        from threading import Thread
        t = Thread(target=self.run)
        t.daemon = True
        t.start()

    def scheduler(self):
        from autoloading.handlers.scheduler import scheduler, camera
        logging.debug(f'开始连接装料点{self.jobid}的料口相机数据！')
        self.jobid = f'loadercamera: {self.index}'
        if scheduler.get_job(self.jobid) is None:
            scheduler.add_job(camera, 'interval', seconds=1, args=(LoaderCamera, LOADING_CAMERA, self.index, self.jobid), id=self.jobid)

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

    def __init__(self, index:int) -> None:
        rtsp = self.license_video_url_list[index]
        super().__init__(rtsp)    
        self.index = index    
        self.start()

    def start(self):
        from threading import Thread
        t = Thread(target=self.run)
        t.daemon = True
        t.start()

    def scheduler(self):
        from autoloading.handlers.scheduler import scheduler, camera
        logging.debug(f'开始连接装料点{self.jobid}的车牌相机数据！')
        self.jobid = f'licenseplatecamera: {self.index}'
        if scheduler.get_job(self.jobid) is None:
            scheduler.add_job(camera, 'interval', seconds=1, args=(LicensePlateCamera, LICENSE_PLATE_CAMERA, self.index, self.jobid), id=self.jobid)

# 装料口摄像头dict
LOADING_CAMERA:dict[int, Camera] = dict()

# 车牌摄像头dict
LICENSE_PLATE_CAMERA:dict[int, Camera] = dict()

