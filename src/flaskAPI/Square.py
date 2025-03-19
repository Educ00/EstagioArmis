from flask_restful import Resource

class Square(Resource):
    def get(self, num):
        return {'Square': num**2}