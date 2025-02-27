import re
import json
import pathlib
import asyncio

import httpx


class _color:
    __slots__ = tuple()
    def __init__(self) -> None:
        pass
    def bold(self,s: str):
        return f"\033[1m{s}\033[0m"
    
    def dim(self,s: str):
        return f"\033[2m{s}\033[0m"
    
    def underline(self,s: str):
        return f"\033[4m{s}\033[0m"
    
    def italic(self,s: str):
        return f"\033[3m{s}\033[0m"
    
    def yellow(self,s: str):
        return f"\033[93m{s}\033[0m"
    
    def cyan(self,s: str):
        return f"\033[96m{s}\033[0m"
    
    def magenta(self,s: str):
        return f"\033[35m{s}\033[0m"
    
    def bright_magenta(self,s: str):
        return f"\033[95m{s}\033[0m"
    
    def red(self,s: str):
        return f"\033[31m{s}\033[0m"
    
    def bright_red(self,s: str):
        return f"\033[91m{s}\033[0m"
    
    def green(self,s: str):
        return f"\033[92m{s}\033[0m"
    
    def blue(self,s: str):
        return f"\033[34m{s}\033[0m"
    
    def bright_yellow(self,s: str):
        return f"\033[93m{s}\033[0m"

color = _color()

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

RESOLUTION_JSON_PATH = pathlib.Path(__file__).parents[1].joinpath("resolutions.json")

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
    
    