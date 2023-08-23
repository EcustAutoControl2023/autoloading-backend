from .base import db
from flask_migrate import Migrate

from .test import Test

migrate = None

def init_app(app):
    global migrate
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@db:3306/autoloading'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db)