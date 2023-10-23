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


# 创建数据库表
models.init_sqlite(app=app)

setup_logging()

# 打印所有路由
with app.app_context():
    logging.info(app.url_map)


from apscheduler.schedulers.background import BackgroundScheduler

def sensor():
    from autoloading.handlers.sensor import read_per_second
    with app.app_context():
        # logging.debug('Scheduler is alive!')
        read_per_second()

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'interval',seconds=1)
sched.start()