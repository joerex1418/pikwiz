import sys
import json
from pathlib import Path

import httpx
from tabulate import tabulate

from src.parse import ImageData
from src.civitai_api import civitai
from src.util import resize_image
from src.util import resize_bulk_from_web
from src.parse import extract_prompt_from_image
from src.parse import parse_prompt_string
from src.color import color
from src.color import cprint
from src.color import console
from PIL.ExifTags import TAGS

def display_8_64_divisors():
    with open("temp.txt", "r") as fp:
        txt = fp.read()
        sizelist = [x.strip() for x in txt.split("\n")]

        data = []
        for size in sizelist:
            w = int(size.split("x")[0].strip())
            h = int(size.split("x")[1].strip())

            divisible_by_8 = ""
            divisible_by_64 = ""

            if w % 8 == 0 and h % 8 == 0:
                divisible_by_8 = "X"

            if w % 64 == 0 and h % 64 == 0:
                divisible_by_64 = "X"
            
            data.append({"Size": f"{w} x {h}", "Div8": divisible_by_8, "Div64": divisible_by_64})
        
        table_string = tabulate(data, headers="keys")

        print(table_string)

        
def generate_civitai_image():
    url = "https://civitai.com/api/trpc/orchestrator.generateImage"
    api = civitai.from_user_config()
    headers = api.auth_headers()
    headers["accept"] = "*/*"
    headers["content-type"] = "application/json"

    json_body = json.loads(Path(__file__).parent.joinpath("temp_body.json").read_text())

    with httpx.Client(headers=headers) as client:
        r = client.request("POST", url=url, headers=headers, json=json_body)
        
        console.print(r)
        
        if r.status_code == 200:
            with Path(__file__).parent.joinpath("temp_response.json").open("w+") as fp:
                json.dump(r.json(), fp, indent=4)


generate_civitai_image()