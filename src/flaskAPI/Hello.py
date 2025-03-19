from flask import request
from flask_restful import Resource


class Hello(Resource):
    def get(self):
        return {'message': 'hello world'}

    def post(self):
        data = request.get_json()
        return {'data': data},201
