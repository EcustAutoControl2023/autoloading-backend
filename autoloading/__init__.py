from flask import Flask, render_template, Response,request,redirect,session
import cv2
from flask_cors import CORS


app = Flask(__name__, static_folder='../static', static_url_path='/static', template_folder='../templates')
app.secret_key = "your_secret_key"
# 开启跨域访问
CORS(app, supports_credentials=True)

# # 初始化api
# handlers.init_app(app=app)

# # 创建数据库表
# models.init_app(app=app)


def generate_frames():
    # video = "http://admin:12345678@192.168.1.11:8083/"
    video = "rtsp://admin:ecust123456@192.168.1.103:554/Streaming/Channels/101?transportmode=unicast"
    capture = cv2.VideoCapture(video)

    while True:
        success, img = capture.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/dl')
def dl():
    return render_template('dl.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username =='admin' and password == 'password':
            session['logged_in'] = True
            return redirect('index')
        else:
            return '无效密码或用户名'
    else:
        return render_template('dl.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

with app.app_context():
    print(app.url_map)

if __name__ == '__main__':
    # 静态文件不缓存
    app.run(debug=True)
