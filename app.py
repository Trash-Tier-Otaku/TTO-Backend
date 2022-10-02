from flask import Flask, jsonify, request
from flask_restful import Api
from routes import Auth, Callback

app = Flask(__name__)
api = Api(app)

api.add_resource(Auth, '/auth')
api.add_resource(Callback, '/callback')
@app.route("/")
def hello():
    return "Hello World!"
