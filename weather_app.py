import datetime as dt
import json
import requests
import os

from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = os.environ["API_TOKEN"]
# you can get API keys for free here - https://api-docs.pgamerx.com/
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]

app = Flask(__name__)

def get_weather(location: str, date: str):
    url_base_url = "https://api.weatherapi.com"
    url_api = "v1"
    url_endpoint = "history.json"

    url = f"{url_base_url}/{url_api}/{url_endpoint}?q={location}&dt={date}&key={WEATHER_API_KEY}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code != 200:
        raise InvalidUsage(json.loads(response.text)['error']['message'], status_code=400)

    return json.loads(response.text)['forecast']['forecastday'][0]['hour'][12]

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
    return "<p><h2>KMA HW1: Python Saas.</h2></p>"

@app.route(
    "/v1/weather",
    methods=["POST"],
)
def weather_endpoint():
    req_data = request.get_json()

    token = req_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    location = req_data.get("location")
    if location == None:
        raise InvalidUsage("Please submit location", status_code=400)
        
    date = req_data.get("date")
    if location == None:
        raise InvalidUsage("Please submit date", status_code=400)

    requester_name = req_data.get("requester_name")
    if location == None:
        raise InvalidUsage("Please submit requester_name", status_code=400)

    weather = get_weather(location, date)

    timestamp = dt.datetime.utcnow()

    result = {
        "requester_name": requester_name,
        "timestamp": timestamp.isoformat(timespec='seconds'),
        "location": location,
        "date": date,
        "weather": {
            "temp_c": weather["temp_c"],
            "wind_kph": weather["wind_kph"],
            "pressure_mb": weather["pressure_mb"],
            "humidity": weather["humidity"]
        }
    }

    return result