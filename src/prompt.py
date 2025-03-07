import re
import json
from pathlib import Path

from .color import console as console
from .civitai_api import bulk_resource_lookup
from .util import parse_weighted_prompt_tags


CIVITAI_SAMPLERS = {
    "Euler a": ["Euler a", "Normal"],
    "DPM++ 2M Karras": ["DPM++ 2M", "Karras"],
    "Euler": ["Euler", "Normal"],
    "Heun": ["Heun", "Normal"],
    "LMS": ["LMS", "Normal"],
    "DDIM": ["DDIM", "Normal"],
    "DPM2": ["DPM2", "Normal"],
    "DPM2 a": ["DPM2 a", "Normal"],
    "Euler a Karras": ["Euler a", "Karras"],
    
    "euler_ancestral": ["Euler a", "Normal"],
}

CIVITAI_MODEL_FILE_TYPES = {
    "SafeTensor": ".safetensors",
    "PickleTensor": ".ckpt",
    "GGUF": ".gguf",
    # "Diffusers"
    # "Core ML": ".zip",
}


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




