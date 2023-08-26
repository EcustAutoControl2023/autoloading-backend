from .base import db


class Test(db.Model):

    test_id = db.Column(db.String(10), primary_key=True)
    test_num = db.Column(db.Integer)