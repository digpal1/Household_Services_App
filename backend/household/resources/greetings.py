from datetime import datetime
from flask import Blueprint, jsonify
from flask_restful import Api, Resource

greeting_bp = Blueprint('greeting_bp', __name__)

api = Api(greeting_bp)

class GreetingApi(Resource):
    def get(self):
        current_time = datetime.now()
        current_hour = current_time.hour
        if current_hour < 12:
            greeting = "Good Morning!"
        elif current_hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"
        return jsonify(greeting)

api.add_resource(GreetingApi, '/greetings')