import io
import sys
import json
import pathlib

import rich
from flask import request
from flask.app import Flask
from flask.json import jsonify
from flask.templating import render_template
from flask_assets import Environment, Bundle


from src import tensorart_api as ta

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# data = ta.search("citron", "MODEL", "HOT_TODAY")
# data = ta.user_models("615037886835732968")
# data = ta.model_details("797480478295782732")

@app.route("/search", methods=["GET"])
def search():
    filters = request.args.get("filters")
    if filters:
        filters = json.loads(filters)
    data = ta.search(
        query=request.args.get("query"),
        _type=request.args.get("type"),
        filters=filters,
        sort_by=request.args.get("sort", request.args.get("sort_by")),
        limit=request.args.get("limit", 20),
        offset=request.args.get("offset", 0),
    )

    return data


@app.route("/model/<model_id>")
def model_details(model_id):
    data = ta.model_details(model_id)
    return data


@app.route("/user/<user_id>")
def user_models(model_id):
    data = ta.user_models(model_id)
    return data

if __name__ == "__main__":
    app.run("127.0.0.1", port=5500, debug=True)