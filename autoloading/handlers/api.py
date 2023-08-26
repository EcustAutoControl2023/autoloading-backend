from flask_restful import Api

from .base import routes
from .test import (
    GetTitle,
    AddNumber
)

api = Api(routes)

api.add_resource(GetTitle, '/title')
api.add_resource(AddNumber, '/add')