import io
import re
import json
import pathlib
import inspect
import asyncio
from html.parser import HTMLParser
from typing import overload as typeoverload

import httpx
from PIL import Image
from PIL.ExifTags import TAGS

from .color import color, cprint


TEST_OUTPUTS = pathlib.Path(__file__).parents[1].joinpath("test-outputs").resolve()

# ---------------------------- #
# Logging
# ---------------------------- #
def log_response(r:httpx.Response):
    if r.status_code in (401, 403):
        colorize = color.red
    elif r.status_code in (400, 404):
        colorize = color.yellow
    elif r.status_code == 429:
        colorize = color.magenta
    else:
        colorize = color.bold
    
    print("{status_code} {urlhost}{urlpath}".format(
        status_code = colorize(f"[{r.status_code}]"),
        urlhost = color.dim(r.url.scheme + r.url.host),
        urlpath = color.magenta(r.url.path)
    ))

def get_line_number():
    return inspect.currentframe().f_back.f_lineno


# ---------------------------- #
# Async Functions
# ---------------------------- #
async def _fetch_request(client:httpx.AsyncClient, req:httpx.Request, **kwargs):
    r = await client.send(req)
    if r.status_code != 200:
        log_response(r)
        return r
    return r

async def _fetch_bulk(request_list:list[httpx.Request], **kwargs):
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=500)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = (asyncio.create_task(_fetch_request(client, req, **kwargs)) for req in request_list)
        responses = await asyncio.gather(*tasks)
        return responses

def fetch_bulk(request_list:list[httpx.Request], **kwargs) -> list[httpx.Response]:
    if isinstance(request_list, httpx.Request):
        request_list = [request_list]
    return asyncio.run(_fetch_bulk(request_list, **kwargs))

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
        "Content-Type": "application/json"
    }


class _ScriptTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_next_data_script = False
        self.script_tag_text = ""

    def handle_starttag(self, tag, attrs):
        # Check for a <script> tag with id="__NEXT_DATA__"
        if tag == "script":
            attr_dict = dict(attrs)
            if attr_dict.get("id") == "__NEXT_DATA__":
                self.in_next_data_script = True

    def handle_data(self, data):
        # If we're inside the correct <script>, collect the data
        if self.in_next_data_script:
            self.script_tag_text += data

    def handle_endtag(self, tag):
        # When closing the <script>, stop collecting data.
        if tag == "script" and self.in_next_data_script:
            self.in_next_data_script = False


# ---------------------------- #
# Prompt parsing functions
# ---------------------------- #
def _calculate_weight(number_of_parentheses:int, decrease:bool=False):
    weight = 1.0
    
    if decrease != True:
        for _ in range(number_of_parentheses):
            weight = weight + (weight * 0.1)
    else:
        for _ in range(number_of_parentheses):
            weight = weight - (weight * 0.1)
    
    return weight


def parse_weighted_prompt_tags(prompt:str) -> dict:
    if not isinstance(prompt, str):
        return {}
    
    weighted_prompt_tags = {}

    # Weight INCREASES
    tag_weights = re.findall(
        r"\(([^()].*?)\)", 
        prompt, 
        re.DOTALL | re.IGNORECASE)

    for t in tag_weights:
        if ":" not in t:
            open_match = re.search(rf"(\(+){re.escape(t)}", prompt, re.IGNORECASE)
            close_match = re.search(rf"{re.escape(t)}(\)+)", prompt, re.IGNORECASE)

            if open_match and close_match:
                open_count = open_match.group().count("(")
                close_count = close_match.group().count(")")
                if open_count == close_count:
                    weight = _calculate_weight(open_count)
                    weight = round(weight, 4)
                    weighted_prompt_tags[t] = {"weight": weight, "type": "implicit"}
        else:
            weight = t.split(":")[1]
            weight = round(float(weight), 4)
            weighted_prompt_tags[t.split(":")[0]] = {"weight": weight, "type": "explicit"}
    
    # Weight DECREASES
    tag_weights_dec = re.findall(
        r"\[([^\[\]].*?)\]", 
        prompt, 
        re.DOTALL | re.IGNORECASE)
    
    for t in tag_weights_dec:
        if ":" not in t:
            open_match = re.search(rf"(\[+){re.escape(t)}", prompt, re.IGNORECASE)
            close_match = re.search(rf"{re.escape(t)}(\]+)", prompt, re.IGNORECASE)

            if open_match and close_match:
                open_count = open_match.group().count("[")
                close_count = close_match.group().count("]")
                if open_count == close_count:
                    weight = _calculate_weight(open_count, decrease=True)
                    weight = round(weight, 4)
                    weighted_prompt_tags[t] = {"weight": weight, "type": "implicit"}
        else:
            weight = t.split(":")[1]
            weight = round(float(weight), 4)
            weighted_prompt_tags[t.split(":")[0]] = {"weight": weight, "type": "explicit"}
    
    return weighted_prompt_tags


# ------------------------------------------ #
# Resolutions
#   - best values divisible by 8
# ------------------------------------------ #

RESOLUTIONS = [
    (262144, 1, 1, "512x512", None),
    (589824, 1, 1, "768x768", None),
    (1048576, 1, 1, "1024x1024", "SDXL"),
    # (2359296, 1, 1, "1536x1536", "SDXL"),
    
    (294912, 1, 2, "384x768", None),
    (524288, 1, 2, "512x1024", None),
    
    (262144, 1, 4, "256x1024", None),
    (589824, 1, 4, "384x1536", None),
    (1048576, 1, 4, "512x2048", "SDXL"),
    
    (393216, 2, 3, "512x768", None),
    (884736, 2, 3, "768x1152", "SDXL"),
    (1038336, 2, 3, "832x1248", "SDXL"),

    (442368, 3, 4, "576x768", None),
    (786432, 3, 4, "768x1024", "SDXL"),
    (995328, 3, 4, "864x1152", "SDXL"),
    (1034880, 3, 4, "880x1176", "SDXL"),
    # (1044288, 3, 4, "888x1176", "SDXL"),
    # (1228800, 3, 4, "960x1280", "SDXL"),

    (327680, 4, 5, "512x640", None),
    (737280, 4, 5, "768x960", "SDXL"),
    (1003520, 4, 5, "896x1120", "SDXL"),
    (1043328, 4, 5, "912x1144", "SDXL"),
    # (1310720, 4, 5, "1024x1280", None),
    
    (258048, 4, 7, "384x672", None),
    (458752, 4, 7, "512x896", None),
    (716800, 4, 7, "640x1120", None),
    (1032192, 4, 7, "768x1344", "SDXL"),

    (983040, 5, 12, "640x1536", "SDXL"),

    (1032192, 7, 9, "896x1152", "SDXL"),

    (252928, 9, 13, "416x608", None),
    (1011712, 9, 13, "832x1216", "SDXL"),

    (466944, 9, 16, "512x912", "SD15"),
    # (746496, 9, 16, "648x1152", "SD21"),
    (1044480, 9, 16, "768x1360", "SDXL"),

    # Irregular ratios
    # (259200, 1.618, 1, "648x400", None),
    # (425984, 1.618, 1, "832x512", None),
    # (660480, 1.618, 1, "1032x640", "SDXL"),
    # (952320, 1.618, 1, "1240x768", "SDXL"),
    # (1036800, 1.618, 1, "1296x800", "SDXL"),


]

RESOLUTION_JSON_PATH = pathlib.Path(__file__).parent.joinpath("resolutions.json")


def generate_resolution_json():
    jsondata = []
    
    for row in RESOLUTIONS:
        if row[1] not in (None, 1.618): # skip irregular sizes
            ar_val_1, ar_val_2 = row[1], row[2]
            res_val_1, res_val_2 = row[3].split("x")
            res_val_1 = int(row[3].split("x")[0])
            res_val_2 = int(row[3].split("x")[1])
            pixels = int(res_val_1 * res_val_2)
            model_rec = row[4]

            if (ar_val_1, ar_val_2) == (1, 1):
                orientations = ("square", )
                aspect_ratios = ("1:1", )
                resolutions = (f"{res_val_1}x{res_val_2}", )
            else:
                orientations = ("portrait", "landscape")
                aspect_ratios = (f"{ar_val_1}:{ar_val_2}", f"{ar_val_2}:{ar_val_1}")
                resolutions = (f"{res_val_1}x{res_val_2}", f"{res_val_2}x{res_val_1}")

            for orientation, aspect_ratio, resolution in zip(orientations, aspect_ratios, resolutions):
                jsondata.append({
                    "pixels": pixels,
                    "aspectRatio": aspect_ratio,
                    "resolution": resolution,
                    "width": int(resolution.split("x")[0]),
                    "height": int(resolution.split("x")[1]),
                    "orientation": orientation,
                    "recommendedModel": model_rec,
                })
    
    with RESOLUTION_JSON_PATH.open("w+") as fp:
        json.dump(jsondata, fp)

    return jsondata


def load_resolution_json():
    with RESOLUTION_JSON_PATH.open("r") as fp:
        return json.load(fp)
    

# ------------------------------------------ #
# Resize Images
# ------------------------------------------ #
def resize_image(source:pathlib.Path|str|bytes, width:int=None, height:int=None) -> Image.Image:
    if isinstance(source, str) and source.startswith("http"):
        url = httpx.URL(source)
        r = httpx.get(url)
        io_bytes = io.BytesIO(r.content)
        source = io_bytes
    
    with Image.open(source) as image:
        if width and height:
            new_size = (width, height)
        else:
            new_size = (image.width // 2, image.height // 2)
        
        new_image = image.resize(new_size)

        # For dev purposes
        # filestem = "output" if save_name == None else save_name
        # filestem = filestem[:filestem.rfind(".")] if filestem.rfind(".") != -1 else filestem

        # image.save(TEST_OUTPUTS.joinpath(f"{filestem}.{image.format.lower()}"), format=image.format)
        
        # new_image.save(TEST_OUTPUTS.joinpath(f"{filestem}-reduced.{image.format.lower()}"), format=image.format)

        return new_image

@typeoverload
def resize_bulk_from_web(urllist, factor:int|float) -> list[Image.Image]:...
@typeoverload
def resize_bulk_from_web(urllist, width:int, height:int) -> list[Image.Image]:...
@typeoverload
def resize_bulk_from_web(urllist, factor:int|float, return_originals:bool=True) -> tuple[list[Image.Image],list[Image.Image]]:...
@typeoverload
def resize_bulk_from_web(urllist, width:int, height:int, return_originals:bool=True) -> tuple[list[Image.Image],list[Image.Image]]:...
def resize_bulk_from_web(urllist, **kwargs) -> list[Image.Image]:
    """
    Only populate width and height arguments if all the original images are 
    the same resolution. Otherwise some of the new images will probably look 
    strange
    """
    width = kwargs.get("width")
    height = kwargs.get("height")
    factor = kwargs.get("factor")

    if not factor and not width and not height:
        raise ValueError("Need 'factor' or 'width' and 'height' parameters populated")

    if factor and factor < 1:
        factor = int(1 // factor)
    else:
        factor = int(factor)
    
    if isinstance(urllist, str):
        urllist = [urllist]

    reqlist = []
    for url in urllist:
        req = httpx.Request("GET", httpx.URL(url))
        reqlist.append(req)

    responses = fetch_bulk(reqlist)
    
    og_image_list = []
    new_image_list = []

    for r in responses:
        io_bytes = io.BytesIO(r.content)

        with Image.open(io_bytes) as image:
            if width and height:
                new_size = (width, height)
            else:
                new_size = (image.width // factor, image.height // factor)
            
            new_image = image.resize(new_size)

            new_image.format = image.format
            new_image.format_description = image.format_description
            new_image.info["exif"] = image.info["exif"]
            new_image.info["url"] = r.url.__str__()

            og_image_list.append(image)
            new_image_list.append(new_image)
    

    if kwargs.get("return_originals") == True:
        return new_image_list, og_image_list

    return new_image_list



