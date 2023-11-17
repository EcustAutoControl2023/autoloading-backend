import logging
from flask import Response
import cv2


def generate_frames(i):
    # 主码流

    #video = "rtsp://admin:1234567a@192.168.100.2:554/h265/ch1/main/av_stream"

    video_url = [
        "rtsp://admin:1234567a@192.168.100.2:554/h265/ch1/main/av_stream",#url_1 装料口1摄像头地址
        "",#url_2
        "",#url_3
        "",#url_4
        "",#url_5
        "",#url_6
        "",#url_7
        "",#url_8
        "",#url_9
        "",#url_10
        "",#url_11
        "",#url_12
        "",#url_13
        "",#url_14
        "",#url_15
        "",#url_16
        "",#url_17
        "",#url_18
        "",#url_19
        "",#url_20    
    ]

    video = video_url[i]


    try:
        capture = cv2.VideoCapture(video)
    except:
        logging.debug('无法连接摄像头')
        capture = None

    if capture is None:
        while True:
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
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