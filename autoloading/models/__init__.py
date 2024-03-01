from .base import db
from flask_migrate import Migrate

migrate = None

def get_db():
    return db

# 初始化数据库
def init_sqlite(app):
    global migrate
    if app.config.get('SQLALCHEMY_DATABASE_URI', None) is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db)
