from flask import jsonify, request
from flask_restful import Resource

class GetTitle(Resource):
    def get(self):
        return jsonify('自动装车系统平台')

class AddNumber(Resource):
    def get(self):
        data = request.args
        sum = 0
        string = list()
        for value in data.values():
            sum += int(value)
            string.append(value)

        return jsonify(f'{string[0]} + {string[1]} = {sum}')
    
    def post(self):
        data = request.get_json()
        sum = 0
        string = list()
        for value in data.values():
            sum += int(value)
            string.append(value)

        return jsonify(f'{string[0]} + {string[1]} = {sum}')