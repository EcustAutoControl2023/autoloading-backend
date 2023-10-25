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
import datetime

def sensor():
    from autoloading.handlers.sensor import read_per_second, start
    with app.app_context():
        logging.debug('Scheduler is alive!')
        read_per_second()

# 只启动一次
scheduler = BackgroundScheduler()
# 添加只执行一次的任务，设置 run_date 为当前时间
scheduler.add_job(sensor, 'date', run_date=datetime.datetime.now())
scheduler.start()