import io
import sys
import json
import pathlib

from flask import request
from flask.app import Flask
from flask.json import jsonify
from flask.templating import render_template
from flask_assets import Environment, Bundle

project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

from src.read import ImageData
from src.prompt import parse_prompt_string
from src.color import color
from src.color import console_color as console
from src.civitai_api import model_lookup
from src.civitai_api import model_version_lookup
from src.civitai_api import bulk_resource_lookup
from src.util import RESOLUTIONS
from src.util import generate_resolution_json, load_resolution_json

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

assets = Environment(app)
scss = Bundle('style.scss', filters='pyscss', output='style.css')
assets.register('style',scss)

# generate_resolution_json()

@app.context_processor
def inject_dict_for_all_templates():
    return {}

@app.route("/")
def index():
    generate_resolution_json()
    resolutions_json = load_resolution_json()
    
    square = [x for x in resolutions_json if x["orientation"] == "square"]
    nonsquare = [x for x in resolutions_json if x["orientation"] != "square"]
    portrait = [x for x in resolutions_json if x["orientation"] == "portrait"]
    landscape = [x for x in resolutions_json if x["orientation"] == "landscape"]

    square_ars = ["1:1"]
    # Only need to filter by 'portrait'; I'll swap on client side
    nonsquare_ars = list({x["aspectRatio"] for x in resolutions_json if x["orientation"] != "portrait"}) 
    
    ar_to_res_map = {"1:1": []}
    for x in resolutions_json:
        if x["orientation"] == "square":
            ar_to_res_map["1:1"].append(x)
        elif x["orientation"] == "portrait": # only need to filter by portrait; I'll swap on client side
            if x["aspectRatio"] not in ar_to_res_map:
                ar_to_res_map[x["aspectRatio"]] = []
            
            ar_to_res_map[x["aspectRatio"]].append(x)

    return render_template('index.html', ar_to_res_map=ar_to_res_map, square=square, nonsquare=nonsquare, portrait=portrait, landscape=landscape, nonsquare_ars=nonsquare_ars)

@app.route("/dev")
def dev():
    path = request.args.get("path")
    if path:
        img = ImageData(f"sample images/{path}")
    else:
        # --------------------- #
        # Testing Images #
        # --------------------- #
        img = ImageData("sample images/5706b224-6b47-404b-8178-d56ce4aed548.jpeg")
        # img = ImageData("sample images/936f0e8d-c76f-4aa7-8b5c-37349f9b7da7.jpeg")
        # img = ImageData("sample images/00058-1310606601.png")
        # img = ImageData("sample images/civitai-dl (multiple loras).jpeg")
        # img = ImageData("sample images/civitai-dl (multiple loras) (og) 2.jpeg")
        # img = ImageData("sample images/civitai-dl (multiple loras) (og).jpeg")
        # img = ImageData("sample images/2025-02-13T15.44.34_1.jpg")
    
    generation_dict = parse_prompt_string(img.raw_prompt)
    
    data = {
        "generation": generation_dict,
        "raw": img.raw_prompt
    }

    return data

@app.route("/extract-prompt", methods=["POST"])
def extract_prompt():
    if "image" not in request.files:
        return jsonify({"error": "No Image Uploaded"}), 400
    
    file = request.files["image"]
    bytes_io = io.BytesIO(file.read())

    img = ImageData(bytes_io)

    generation_dict = parse_prompt_string(img.raw_prompt)
    
    data = {
        "generation": generation_dict,
        "raw": img.raw_prompt
    }

    with open("temp.json", "w+") as fp:
        json.dump(data, fp)

    return data

@app.route("/lookup/civitai-model", methods=["GET"])
def civitai_model():
    model_id = request.args.get("model_id")
    model_version_id = request.args.get("model_version_id")
    model_version_ids = request.args.get("model_version_ids")

    if model_version_ids:
        model_version_ids = [x.strip() for x in model_version_ids.split(",")]
        data = bulk_resource_lookup(model_version_ids)

    elif model_id:
        data = model_lookup(model_id)
    elif model_version_id:
        data = model_version_lookup(model_version_id)
    else:
        data = {}
    
    return data

if __name__ == "__main__":
    app.run("127.0.0.1", port=5500, debug=True)