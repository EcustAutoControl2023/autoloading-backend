from flask import Flask
from .index import (
    index1,
    index2,
    index3,
    index4,
    index5,
    index6,
    index7,
    index8,
    index9,
    index10,
    index11,
    index12,
    index13,
    index14,
    index15,
    index16,
    index17,
    index18,
    index19,
    index20,
    overview
)

from .login import (
    login
)

from .video import (
    video_feed_new,
    license_video_feed_new
)

from .app import(
    connect,
)

from .socket import(
    socketio
)


# 集成路由
def init_app(app:Flask):
    socketio.init_app(app=app, cors_allowed_origins='*')
    app.add_url_rule('/', endpoint='login', view_func=login, methods=['GET','POST'])
    app.add_url_rule('/login', endpoint='login', view_func=login)
    app.add_url_rule('/index1', endpoint='index1', view_func=index1)
    app.add_url_rule('/index2', endpoint='index2', view_func=index2)
    app.add_url_rule('/index3', endpoint='index3', view_func=index3)
    app.add_url_rule('/index4', endpoint='index4', view_func=index4)
    app.add_url_rule('/index5', endpoint='index5', view_func=index5)
    app.add_url_rule('/index6', endpoint='index6', view_func=index6)
    app.add_url_rule('/index7', endpoint='index7', view_func=index7)
    app.add_url_rule('/index8', endpoint='index8', view_func=index8)
    app.add_url_rule('/index9', endpoint='index9', view_func=index9)
    app.add_url_rule('/index10', endpoint='index10', view_func=index10)
    app.add_url_rule('/index11', endpoint='index11', view_func=index11)
    app.add_url_rule('/index12', endpoint='index12', view_func=index12)
    app.add_url_rule('/index13', endpoint='index13', view_func=index13)
    app.add_url_rule('/index14', endpoint='index14', view_func=index14)
    app.add_url_rule('/index15', endpoint='index15', view_func=index15)
    app.add_url_rule('/index16', endpoint='index16', view_func=index16)
    app.add_url_rule('/index17', endpoint='index17', view_func=index17)
    app.add_url_rule('/index18', endpoint='index18', view_func=index18)
    app.add_url_rule('/index19', endpoint='index19', view_func=index19)
    app.add_url_rule('/index20', endpoint='index20', view_func=index20)
    app.add_url_rule('/overview', endpoint='overview', view_func=overview)
    app.add_url_rule('/connect', endpoint='connect',view_func=connect, methods=['POST'])
    app.add_url_rule('/video_feed_new/<video_id>', endpoint='video_feed_new', view_func=video_feed_new)
    app.add_url_rule('/license_video_feed_new/<license_video_id>', endpoint='license_video_feed_new', view_func=license_video_feed_new)
