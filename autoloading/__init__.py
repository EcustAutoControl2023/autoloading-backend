from flask import Flask, jsonify, session
from flask_cors import CORS
from autoloading import (
    handlers,
    models
)
from flask_socketio import SocketIO
from .config import *


app = Flask(__name__, static_folder='../static', static_url_path='/static', template_folder='../templates')
app.secret_key = SECRET_KEY
# 开启跨域访问
CORS(app, supports_credentials=True)

# 初始化api
handlers.init_app(app=app)

socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('connect')
def test_connect():
    # emit('my response', {'data': 'Connected'})
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# 车牌弹窗
def truck_id_popup(data):
    global socketio
    socketio.emit('truck_id_popup', data)

@socketio.on('truck_id_popup_confirm')
def truck_id_popup_confirm(confirm):
    global TRUCK_CONFIRM
    session['truck_id_popup_confirm'] = confirm['data']
    TRUCK_CONFIRM.put(confirm['data']) 

# 中控弹窗
def center_popup(data):
    global socketio
    socketio.emit('center_popup', data)

@socketio.on('center_popup_confirm')
def center_popup_confirm(confirm):
    global TRUCK_CONFIRM
    session['center_popup_confirm'] = confirm['data']
    TRUCK_CONFIRM.put(confirm['data']) 

# 创建数据库表
models.init_sqlite(app=app)

# 打印所有路由
with app.app_context():
    print(app.url_map)

if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app,debug=True)
