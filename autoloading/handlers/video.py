from flask import Response
import cv2

def generate_frames():
    # video = 'rtsp://admin:12345678@10.103.155.112:8554/live'
    # 主码流
    # video = "rtsp://admin:1234567a@192.168.100.2:554/h264/ch1/main/av_stream"
    # 子码流
    # video ="rtsp://admin:1234567a@192.168.100.2:554/mjpeg/ch1/sub/av_stream"
    video = "rtsp://admin:1234567a@192.168.100.2:554/h265/ch1/sub/av_stream"

    try:
        capture = cv2.VideoCapture(video)
    except:
        print('无法连接摄像头')

    while True:
        success, img = capture.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')