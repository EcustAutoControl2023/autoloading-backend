from flask import Flask
from flask_cors import CORS
from autoloading import (
    handlers,
    models
)
from .config import *
from autoloading.handlers.scheduler import schedulers_start


app = Flask(__name__, static_folder='../static', static_url_path='/static', template_folder='../templates')
app.secret_key = SECRET_KEY


# 开启跨域访问
CORS(app, supports_credentials=True)

# 初始化api
handlers.init_app(app=app)


# 创建数据库表
models.init_sqlite(app=app)
# models.init_mysql(app=app)

setup_logging()

# 打印所有路由
with app.app_context():
    logging.info(app.url_map)

# 启动后台定时任务(读传感器)
schedulers_start(app=app)

from autoloading.handlers.loaderpoint import load_point_dict, create_loader_points
logging.debug("=======================")

logging.debug(load_point_dict)
