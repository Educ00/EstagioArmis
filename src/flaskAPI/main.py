from flask import Flask, jsonify, request
from flask_restful import Api
from Hello import Hello
from Square import Square
app = Flask(__name__)
api = Api(app)

api.add_resource(Hello, '/')
api.add_resource(Square, '/square/<int:num>')

if __name__ == '__main__':
    app.run(port=5400,debug=True)