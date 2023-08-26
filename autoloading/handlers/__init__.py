from autoloading.handlers.base import routes
from autoloading.handlers.api import api


def init_app(app):

    @app.route('/')
    def index():
        return 'Hello, World!'

    app.register_blueprint(routes, url_prefix='/api')
    api.init_app(app)