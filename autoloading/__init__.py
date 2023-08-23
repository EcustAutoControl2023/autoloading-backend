from flask import Flask
from flask_cors import CORS
from autoloading import(
    handlers,
    models
)


app = Flask(__name__)
# 开启跨域访问
CORS(app, supports_credentials=True)

# 初始化api
handlers.init_app(app=app)

# 数据库表
from time import sleep
# 7s 后启动
sleep(7)
models.init_app(app=app)