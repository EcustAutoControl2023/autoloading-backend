from .base import db
from flask_migrate import Migrate

from .sensor import Sensor

migrate = None

# 初始化数据库
def init_sqlite(app):
    global migrate
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db)
