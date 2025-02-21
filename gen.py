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


@app.route("/")
def index():
    data = ta.model_details_bulk(["711252739176336907", "819251341101824139"])
    return data


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


@app.route("/image/<image_id>")
def get_image_details(image_id):
    post_id = request.args.get("post_id", request.args.get("postId"))
    data = ta.image_details(image_id, post_id)

    if request.args.get("parse") == "true":
        data = ta.parse_image_parameters(data)

    return data


@app.route("/model/<model_id>")
def get_model_details(model_id):
    data = ta.model_details(model_id)
    return data


@app.route("/user/<user_id>")
def get_user_models(model_id):
    data = ta.user_models(model_id)
    return data



if __name__ == "__main__":
    app.run("127.0.0.1", port=5000, debug=True)