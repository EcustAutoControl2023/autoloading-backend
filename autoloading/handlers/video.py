import logging
from flask import Response
import cv2

import threading, time
from autoloading.config import LOADER, CAP_TIME_OUT


# 减少摄像头连接不上超时等待问题
class videocapture_Thread(threading.Thread):
    def __init__(self, rtsp):
        super(videocapture_Thread, self).__init__()
        self.result = None
        self.rtsp = rtsp

    def run(self):
        self.result = self.open_videocapture()

    def open_videocapture(self):
        cap = cv2.VideoCapture(self.rtsp)
        if cap.isOpened():
            return cap
        else:
            cap.release()
            return None

def generate_frames(i):
    # 主码流

    #video = "rtsp://admin:1234567a@192.168.100.2:554/h265/ch1/sub/av_stream"

    video_url = [
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

    video = video_url[i]

    capture = None

    time_out = CAP_TIME_OUT
    start = time.time()
    cap_thread = videocapture_Thread(video)
    cap_thread.daemon = True
    cap_thread.start()
    cap_thread.join(timeout=time_out)
    logging.debug(f'摄像头链接超时时间:{time.time() - start}')
    capture = cap_thread.result

    if capture is None:
        logging.debug(f'装料点({LOADER}): 无法连接摄像头')

    if capture is None:
        # while True:
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'+ b'\r\n')
    else:
        while True:
            success, img = capture.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            

def video_feed():
    return Response(generate_frames(0), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed1():
    return Response(generate_frames(1), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed2():
    return Response(generate_frames(2), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed3():
    return Response(generate_frames(3), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed4():
    return Response(generate_frames(4), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed5():
    return Response(generate_frames(5), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed6():
    return Response(generate_frames(6), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed7():
    return Response(generate_frames(7), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed8():
    return Response(generate_frames(8), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed9():
    return Response(generate_frames(9), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed10():
    return Response(generate_frames(10), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed11():
    return Response(generate_frames(11), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed12():
    return Response(generate_frames(12), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed13():
    return Response(generate_frames(13), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed14():
    return Response(generate_frames(14), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed15():
    return Response(generate_frames(15), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed16():
    return Response(generate_frames(16), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed17():
    return Response(generate_frames(17), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed18():
    return Response(generate_frames(18), mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed19():
    return Response(generate_frames(19), mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_license_frames(i):

    video_url = [
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

    video = video_url[i]
    capture = None

    time_out = CAP_TIME_OUT
    start = time.time()
    cap_thread = videocapture_Thread(video)
    cap_thread.daemon = True
    cap_thread.start()
    cap_thread.join(timeout=time_out)
    logging.debug(f'车牌摄像头链接超时时间:{time.time() - start}')
    capture = cap_thread.result

    if capture is None:
        logging.debug(f'装料点({LOADER}): 无法连接车牌摄像头')

    if capture is None:
        # while True:
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'+ b'\r\n')
    else:
        while True:
            success, img = capture.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def license_video_feed():
    return Response(generate_license_frames(0), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed1():
    return Response(generate_license_frames(1), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed2():
    return Response(generate_license_frames(2), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed3():
    return Response(generate_license_frames(3), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed4():
    return Response(generate_license_frames(4), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed5():
    return Response(generate_license_frames(5), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed6():
    return Response(generate_license_frames(6), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed7():
    return Response(generate_license_frames(7), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed8():
    return Response(generate_license_frames(8), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed9():
    return Response(generate_license_frames(9), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed10():
    return Response(generate_license_frames(10), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed11():
    return Response(generate_license_frames(11), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed12():
    return Response(generate_license_frames(12), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed13():
    return Response(generate_license_frames(13), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed14():
    return Response(generate_license_frames(14), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed15():
    return Response(generate_license_frames(15), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed16():
    return Response(generate_license_frames(16), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed17():
    return Response(generate_license_frames(17), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed18():
    return Response(generate_license_frames(18), mimetype='multipart/x-mixed-replace; boundary=frame')

def license_video_feed19():
    return Response(generate_license_frames(19), mimetype='multipart/x-mixed-replace; boundary=frame')
