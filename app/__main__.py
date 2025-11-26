import io
import sys
import json
import pathlib

import pyperclip
from flask import request, send_file
from flask.app import Flask
from flask.json import jsonify
from flask.templating import render_template
from flask_assets import Environment, Bundle

project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# from src.parse import ImageData
# from src.parse import parse_prompt_string
from src.color import color
from src.color import console as console
from src.api import extract_prompt_from_image
from src.api import parse_prompt_string
# from src.civitai_api import civitai
# from src.civitai_api import model_lookup
# from src.civitai_api import model_version_lookup
# from src.civitai_api import bulk_resource_lookup
# from src.util import RESOLUTIONS
# from src.util import generate_resolution_json, load_resolution_json
# from src.civitai_constants import BaseModel, CheckpointType, FileFormat, ModelSort, ModelType, Period, Sort, GenTag, Technique, Tool

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

assets = Environment(app)
main_scss = Bundle('style.scss', filters='pyscss', output='style.css')
assets.register('main', main_scss)
tagit_scss = Bundle('tagit.scss', filters='pyscss', output='tagit.css')
assets.register('tagit', tagit_scss)

# generate_resolution_json()

@app.context_processor
def inject_dict_for_all_templates():
    return {}

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/load-directory")
def load_directory():
    path = request.args.get("path")
    sort_by = request.args.get("sort", "created").lower().strip()
    if path == None or path == "":
        return "Error. Provide a path, bish"
    
    path = pathlib.Path(path).resolve()
    directory_items = list(path.iterdir())
    
    if sys.platform == "darwin":
        correct_attribute = "st_birthtime"
    elif sys.platform == "win32":
        correct_attribute = "st_ctime"
    elif sys.platform == "linux":
        ...

    if sort_by == "created" or sort_by == "modified":
        directory_items = sorted(directory_items, key=lambda x: getattr(x.stat(), correct_attribute))

    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    image_files = []
    for fileitem in directory_items:
        if fileitem.suffix.lower() in IMAGE_EXTS:
            size = fileitem.stat().st_size
            size_display = None

            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if size < 1024:
                    size_display = f"{size:.2f} {unit}"
                    break
                size /= 1024

            image_files.append({
                "name": fileitem.name,
                "type": fileitem.suffix,
                "fullPath": fileitem.resolve().__str__(),
                "fullDirPath": fileitem.parent.resolve().__str__(),
                "sizeDisplay": size_display,
                "size": size,
                "createdDisplay": "TBD",
                "created": getattr(fileitem.stat(), correct_attribute)
            })
    
    return image_files


@app.route("/manual_load")
def manual_load():
    path = request.args.get("path")
    if path:
        path = pathlib.Path(path).name
        img = ImageData(f"sample images/{path}")

    generation_dict = parse_prompt_string(img.raw_prompt)

    data = {
        "generation": generation_dict,
        "raw": img.raw_prompt
    }

    return data

@app.route("/civitai-dev")
def civitai_dev():
    api = civitai.from_user_config()
    # data = api.get_generation_queue(tags=[Tag.DISLIKED])
    # data = api.get_all_generations(tags=[Tag.DISLIKED])
    # data = api.get_images(techniques=["inpainting"])
    # data = api.get_user("FanofAnime99")
    # data = api.get_user("novowels")
    # data = api.get_user_models("novowels", sort_by="Highest Rated")
    # data = api.get_model_alt(24779)
    # data = api.get_user_posts("FanofAnime99", sort_by=PostSort.NEWEST, section="draft")
    # data = api.get_user_posts("novowels", sort_by=PostSort.NEWEST, period=Period.MONTH)
    # data = api.get_user_images("FanofAnime99", sort_by=PostSort.NEWEST, section="draft")
    # data = api.get_user_hidden_settings()
    # data = api.get_account_settings()
    # data = api.get_account_buzz()
    # data = api.get_user_images(sort_by=PostSort.NEWEST, section="draft")
    # data = api.get_images()
    # data = api.account_settings
    # data = api.get_tools()
    # data = api.get_generation_queue()
    # data = api.get_all_generations()
    # data = api.get_image_generation_data(60630705)
    # data = api.get_model(24779)
    data = api.get_model_version(93208)
    # data = api.me()
    # data = api.get_tools()

    return data

@app.route("/extract-prompt2", methods=["POST"])
def extract_prompt2():
    filepath = request.json.get("fullpath")
    img = extract_prompt_from_image(filepath)
    data = parse_prompt_string(img)

    return data

@app.route("/image")
def image():
    path = request.args.get("path")
    path = pathlib.Path(path)
    return send_file(path)


@app.route("/extract-prompt", methods=["POST"])
def extract_prompt():
    if "image" not in request.files:
        return jsonify({"error": "No Image Uploaded"}), 400
    
    file = request.files["image"]
    bytes_io = io.BytesIO(file.read())

    img = ImageData(bytes_io)

    generation_dict = parse_prompt_string(img.raw_prompt)
    import rich
    # rich.print_json(data=generation_dict)
    
    data = {
        "generation": generation_dict,
        "raw": img.raw_prompt
    }

    # with open("temp.json", "w+") as fp:
    #     json.dump(data, fp)

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

@app.route("/tagit", methods=["GET", "POST"])
def tagit():
    if request.method == "GET":
        return render_template("tagit.html")
    
    elif request.method == "POST":
        images = request.files.getlist("images")
        
        return_data = []
        for imagefile in images:
            bytes_io = io.BytesIO(imagefile.read())
            try:
                image_data = ImageData(bytes_io)
                gendict = parse_prompt_string(image_data.raw_prompt, prompts_only=True)
                
                return_data.append({
                    "filename": imagefile.filename,
                    "tagtext": gendict.get("positive")
                })
            except Exception as e:
                console.log(e)
        
        return return_data


if __name__ == "__main__":
    app.run("localhost", port=5550, debug=True)