import json

import requests
from flask import Flask, jsonify, request


API_TOKEN = ""

API_KEY = ""

app = Flask(__name__)


def generate_weather(location, date, requester_name):
    url_base = "http://api.weatherapi.com/v1/history.json"

    url = f"{url_base}?key={API_KEY}&q={location}&dt={date}"

    response = requests.get(url)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    location = ""
    if json_data.get("location"):
        location = json_data.get("location")

    date = ""
    if json_data.get("date"):
        date = json_data.get("date")

    requester_name = ""
    if json_data.get("requester_name"):
        requester_name = json_data.get("requester_name")

    weather = generate_weather(location, date, requester_name)


    result = {
        "requester_name": requester_name,
        "timestamp": weather['forecast']['forecastday'][0]['hour'][12]['time'],
        "location": location,
        "date": date,
        "weather": {
            "temp_c": weather['forecast']['forecastday'][0]['hour'][12]['temp_c'],
            "wind_kph": weather['forecast']['forecastday'][0]['hour'][12]['wind_kph'],
            "pressure_mb": weather['forecast']['forecastday'][0]['hour'][12]['pressure_mb'],
            "humidity": weather['forecast']['forecastday'][0]['hour'][12]['humidity'],
            "feelslike_c": weather['forecast']['forecastday'][0]['hour'][12]['feelslike_c'],
            "cloud": weather['forecast']['forecastday'][0]['hour'][12]['cloud']
        }
    }

    return result