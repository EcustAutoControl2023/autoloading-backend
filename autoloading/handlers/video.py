from flask import Response
import cv2

def generate_frames():
    # 主码流
    # video = "rtsp://admin:ecust123456@192.168.1.103:554/h264/ch1/main/av_stream"
    # 子码流
    # video = "rtsp://admin:ecust123456@192.168.1.103:554/h264/ch1/sub/av_stream"
    video ="rtsp://admin:ecust123456@192.168.1.103:554/mjpeg/ch1/sub/av_stream"

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