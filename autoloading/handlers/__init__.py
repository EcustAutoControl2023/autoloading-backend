from flask import Flask
from .index import (
    index,
    login,
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
)
from .dl import (
    dl
)
from .video import (
    video_feed,
    video_feed1,
    video_feed2,
    video_feed3,
    video_feed4,
    video_feed5,
    video_feed6,
    video_feed7,
    video_feed8,
    video_feed9,
    video_feed10,
    video_feed11,
    video_feed12,
    video_feed13,
    video_feed14,
    video_feed15,
    video_feed16,
    video_feed17,
    video_feed18,
    video_feed19,
)
from .app import(
    connect,
    clear_session
)
from .sensor import(
    start,
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
    app.add_url_rule('/video_feed1', endpoint='video_feed1', view_func=video_feed1)
    app.add_url_rule('/video_feed2', endpoint='video_feed2', view_func=video_feed2)
    app.add_url_rule('/video_feed3', endpoint='video_feed3', view_func=video_feed3)
    app.add_url_rule('/video_feed4', endpoint='video_feed4', view_func=video_feed4)
    app.add_url_rule('/video_feed5', endpoint='video_feed5', view_func=video_feed5)
    app.add_url_rule('/video_feed6', endpoint='video_feed6', view_func=video_feed6)
    app.add_url_rule('/video_feed7', endpoint='video_feed7', view_func=video_feed7)
    app.add_url_rule('/video_feed8', endpoint='video_feed8', view_func=video_feed8)
    app.add_url_rule('/video_feed9', endpoint='video_feed9', view_func=video_feed9)
    app.add_url_rule('/video_feed10', endpoint='video_feed10', view_func=video_feed10)
    app.add_url_rule('/video_feed11', endpoint='video_feed11', view_func=video_feed11)
    app.add_url_rule('/video_feed12', endpoint='video_feed12', view_func=video_feed12)
    app.add_url_rule('/video_feed13', endpoint='video_feed13', view_func=video_feed13)
    app.add_url_rule('/video_feed14', endpoint='video_feed14', view_func=video_feed14)
    app.add_url_rule('/video_feed15', endpoint='video_feed15', view_func=video_feed15)
    app.add_url_rule('/video_feed16', endpoint='video_feed16', view_func=video_feed16)
    app.add_url_rule('/video_feed17', endpoint='video_feed17', view_func=video_feed17)
    app.add_url_rule('/video_feed18', endpoint='video_feed18', view_func=video_feed18)
    app.add_url_rule('/video_feed19', endpoint='video_feed19', view_func=video_feed19)
    app.add_url_rule('/index', endpoint='index', view_func=index)
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
    app.add_url_rule('/connect', endpoint='connect',view_func=connect, methods=['POST'])
    app.add_url_rule('/clear_session', view_func=clear_session,endpoint='clear_session', methods=['GET'])
    app.add_url_rule('/start', endpoint='start', view_func=start)
    app.add_url_rule('/stop', endpoint='stop', view_func=stop)
    app.add_url_rule('/store', endpoint='truck_content', view_func=insert_truck_content,methods=['POST'])
