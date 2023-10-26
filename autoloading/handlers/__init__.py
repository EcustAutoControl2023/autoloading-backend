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
    start,
    restart,
    stop,
)
from .socket import(
    socketio
)
from .truck_store import(
    insert_truck_content
)




# 集成路由
def init_app(app:Flask):
    socketio.init_app(app=app, cors_allowed_origins='*')
    app.add_url_rule('/', endpoint='login', view_func=login, methods=['GET','POST'])
    app.add_url_rule('/dl', endpoint='dl', view_func=dl)
    app.add_url_rule('/video_feed', endpoint='video_feed', view_func=video_feed)
    app.add_url_rule('/index', endpoint='index', view_func=index)
    app.add_url_rule('/connect', endpoint='connect',view_func=connect, methods=['POST'])
    app.add_url_rule('/clear_session', view_func=clear_session,endpoint='clear_session', methods=['GET'])
    app.add_url_rule('/start', endpoint='start', view_func=start)
    app.add_url_rule('/restart', endpoint='restart', view_func=restart)
    app.add_url_rule('/stop', endpoint='stop', view_func=stop)
    app.add_url_rule('/store', endpoint='truck_content', view_func=insert_truck_content,methods=['POST'])
