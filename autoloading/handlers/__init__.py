from flask import Flask
# from autoloading.handlers.base import routes
# from autoloading.handlers.api import api
from .video import video_feed
from .index import (
    index,
    login
)
from .dl import dl


def init_app(app:Flask):

    # @app.route('/')
    # def index():
    #     return 'Hello, World!'
    # app.register_blueprint(routes, url_prefix='/api')
    # api.init_app(app)
    app.add_url_rule('/video_feed', endpoint='video_feed', view_func=video_feed)
    app.add_url_rule('/index', endpoint='index', view_func=index)
    app.add_url_rule('/dl', endpoint='dl', view_func=dl)
    app.add_url_rule('/', endpoint='login', view_func=login, methods=['GET','POST'])