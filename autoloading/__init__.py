from flask import Flask
from flask_cors import CORS
from autoloading import (
    handlers,
    models
)
from .config import *
from autoloading.handlers.scheduler import schedulers_start

def create_app(test_config=None):
    app = Flask(__name__, static_folder='../static', static_url_path='/static', template_folder='../templates')
    app.secret_key = SECRET_KEY

    if test_config is not None:
        app.config.update(test_config)

    # 开启跨域访问
    CORS(app, supports_credentials=True)

    # 初始化api
    handlers.init_app(app=app)

    # 创建数据库表
    models.init_sqlite(app=app)
    # models.init_mysql(app=app)

    # 启动后台定时任务(读传感器)
    schedulers_start(app=app)

    return app


setup_logging()


if __name__ == '__main__':

    app = create_app()

    # 打印所有路由
    with app.app_context():
        logging.info(app.url_map)
