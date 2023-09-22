from flask import Flask
from .index import (
    index,
    login,
)
from .dl import (
    dl
)
from .video import (
    video_feed
)
from .app import(
    connect,
    clear_session
)
from .sensor import(
    test_save_data,
    test_read_data
)
from .socket import(
    socketio
)


def init_app(app:Flask):
    socketio.init_app(app=app, cors_allowed_origins='*')
    app.add_url_rule('/', endpoint='login', view_func=login, methods=['GET','POST'])
    app.add_url_rule('/dl', endpoint='dl', view_func=dl)
    app.add_url_rule('/video_feed', endpoint='video_feed', view_func=video_feed)
    app.add_url_rule('/index', endpoint='index', view_func=index)
    app.add_url_rule('/connect', view_func=connect,endpoint='connect', methods=['POST'])
    app.add_url_rule('/clear_session', view_func=clear_session,endpoint='clear_session', methods=['GET'])
    app.add_url_rule('/test_save_data', view_func=test_save_data,endpoint='test_save_data', methods=['GET'])
    app.add_url_rule('/test_read_data', view_func=test_read_data,endpoint='test_read_data', methods=['GET'])