import json
from typing import Literal

import httpx

from .util import fetch_bulk
from .util import get_headers
from .util import parse_weighted_prompt_tags
from .color import console as console


def search(query, _type:Literal["MODEL", "USER", "TAG", "WORKFLOW_TEMPLATE"], filters:dict=None, sort_by:Literal["MOST_RUN", "HOT_TODAY", "NEWEST"]=None, limit:int=20, offset:int=0):
    url = "https://api.tensor.art/community-web/v1/search/general/v2"

    headers = get_headers()

    data = {
        "query": query, 
        "visibility": "ORDINARY", 
        "type": _type, 
        "sort": sort_by,
        "limit": limit, 
        "offset": offset,
    }

    if filters:
        data["filter"] = filters

    with httpx.Client() as client:
        client.headers.update(headers)
        
        r = client.post(url, json=data)

        response_data = r.json()
        
        return response_data
    
def user_models(user_id:str, sort_by: Literal["NEWEST", "MOST_RUN"]=None, limit:int=20, offset:int=0, subscriber_only:bool=False):
    url = "https://api.tensor.art/community-web/v1/project/user/list"

    headers = get_headers()

    sort_by = "NEWEST" if sort_by == None else sort_by

    data = {
        "userId": user_id, 
        "visibility": "ORDINARY", 
        "sort": sort_by,
        "subscriberOnly": subscriber_only,
        "visibilityGte": "PRIVATE",
        "limit": limit, 
        "offset": offset
    }

    with httpx.Client() as client:
        client.headers.update(headers)
        
        r = client.post(url, json=data)

        response_data = r.json()
        
        return response_data
    
def user_posts():
    """
    curl 'https://api.tensor.art/community-web/v1/post/list' \

    -H 'Referer: https://tensor.art/u/610682227356869499' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0' \
    -H 'Content-Type: application/json' \
    --data-raw '{"cursor":"1","filter":{},"size":"20","userId":"610682227356869499","sort":"NEWEST","visibility":"PRIVATE"}'
    """

def image_details(image_id:str, post_id:str=None):
    url = "https://api.tensor.art/community-web/v1/image/detail"
    
    headers = get_headers()

    params = {
        "id": image_id
    }

    if post_id != None:
        params["postId"] = post_id

    with httpx.Client() as client:
        client.headers.update(headers)
        r = client.get(url, params=params)
    
    response_data = r.json()

    return response_data

def model_details(model_id:str):
    url = "https://api.tensor.art/community-web/v1/model/detail"

    headers = get_headers()

    params = {"modelId": model_id}

    with httpx.Client() as client:
        client.headers.update(headers)
        r = client.get(url, params=params)
    
    response_data = r.json()

    return response_data

def model_details_bulk(model_ids:list):
    reqlist = []
    
    url = "https://api.tensor.art/community-web/v1/model/detail"
    headers = get_headers()

    for model_id in model_ids:
        params = {"modelId": model_id}
        req = httpx.Request("GET", url, params=params, headers=headers)
        reqlist.append(req)

    responses = fetch_bulk(reqlist)

    return [r.json() for r in responses]


def parse_image_parameters(image_details_response:dict):
    image_details_dict = image_details_response.get("data", {}).get("image", {})
    og_gendata: dict = image_details_dict.get("generationData")
    assert(og_gendata)

    settings_dict = {
        "steps": None,
        "cfg_scale": None,
        "seed": None,
        "size": None,
        "sampler": None,
        "schedule_type": None,
        "vae": None,
        "model": None,
    }

    if (og_gendata["type"], og_gendata["workspaceType"]) == ("TENSOR_ART_V1", "SDWEBUI"):
        tensor_art_data: dict = og_gendata["tensorArtV1"]
        
        positive_prompt = tensor_art_data.get("prompt")
        negative_prompt = tensor_art_data.get("negativePrompt")
        lora_weights = []
        embed_weights = []

        base_model_dict = tensor_art_data.get("baseModel", {})
        checkpoint_id = base_model_dict.get("modelId")
        checkpoint_dict = image_details_dict.get("models", {}).get(checkpoint_id)
        # checkpoint_name = checkpoint_dict.get("projectName")
        # checkpoint_filename = base_model_dict.get("modelFileName")

        tensorart_resources = []
        for resource_data in image_details_dict.get("models", {}).values():
            resource_id = resource_data.get("id")
            
            ta_resource = {}

            if resource_data.get("type") == "CHECKPOINT":
                ta_resource["type"] = "checkpoint"
                ta_resource["base_model"] = resource_data.get("baseModel")
                ta_resource["model_id"] = resource_id
                ta_resource["model_name"] = resource_data.get("projectName")
                ta_resource["model_version_name"] = resource_data.get("name")
                ta_resource["model_filename"] = base_model_dict.get("modelFileName")
            elif resource_data.get("type") == "LORA":
                ta_resource["type"] = "lora"
                ta_resource["base_model"] = resource_data.get("baseModel")
                ta_resource["model_id"] = resource_id
                ta_resource["model_name"] = resource_data.get("projectName")
                ta_resource["model_version_name"] = resource_data.get("name")
                for m in tensor_art_data.get("models", []):
                    if m["modelId"] == resource_id:
                        ta_resource["model_filename"] = m["modelFileName"]
                        lora_weights.append([ta_resource["model_filename"], m["weight"]])
                        break
            elif resource_data.get("type") == "EMBEDDING":
                ta_resource["type"] = "embed"
                ta_resource["base_model"] = resource_data.get("baseModel")
                ta_resource["model_id"] = resource_id
                ta_resource["model_name"] = resource_data.get("projectName")
                ta_resource["model_version_name"] = resource_data.get("name")
                for m in tensor_art_data.get("embeddingModels", []):
                    if m["modelId"] == resource_id:
                        ta_resource["model_filename"] = m["modelFileName"]
                        embed_weights.append([ta_resource["model_filename"], m["weight"]])
                        break

            tensorart_resources.append(ta_resource)
        
        settings_dict["steps"] = str(tensor_art_data.get("steps")) if tensor_art_data.get("steps") != None else None
        settings_dict["cfg_scale"] = tensor_art_data.get("cfgScale")
        settings_dict["seed"] = str(tensor_art_data.get("seed")) if tensor_art_data.get("seed") != None else None
        settings_dict["size"] = f"{tensor_art_data['width']}x{tensor_art_data['height']}"
        settings_dict["clip_skip"] = tensor_art_data.get("clipSkip")
        settings_dict["sampler"] = tensor_art_data.get("samplerName")
        settings_dict["schedule_type"] = tensor_art_data.get("schedule")
        settings_dict["vae"] = tensor_art_data.get("sdVae")
        settings_dict["model"] = checkpoint_dict.get("projectName")
        settings_dict["_ksamplerName"] = tensor_art_data.get("ksamplerName")
        settings_dict["_guidance"] = tensor_art_data.get("guidance")

    positive_prompt_weight_tags = parse_weighted_prompt_tags(positive_prompt)
    negative_prompt_weight_tags = parse_weighted_prompt_tags(negative_prompt)

    generation_data = {
        "positive": positive_prompt,
        "negative": negative_prompt,
        "loras": lora_weights,
        "embeds": embed_weights,
        "custom_tag_weights": {
            "positive": positive_prompt_weight_tags,
            "negative": negative_prompt_weight_tags
        }, 
        "settings": settings_dict,
        "tensorart_resources": tensorart_resources,
        "tensorart_metadata": {},
    }

    data = {
        "generation": generation_data,
        "raw": None
    }

    return data



    