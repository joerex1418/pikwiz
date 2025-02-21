import json
from typing import Literal

import httpx

from .color import console_color as console


def search(query, _type:Literal["MODEL", "USER", "TAG", "WORKFLOW_TEMPLATE"], filters:dict=None, sort_by:Literal["MOST_RUN", "HOT_TODAY", "NEWEST"]=None, limit:int=20, offset:int=0):
    url = "https://api.tensor.art/community-web/v1/search/general/v2"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
        "Content-Type": "application/json"
    }

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

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
        "Content-Type": "application/json"
    }

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


def model_details(model_id:str):
    url = "https://api.tensor.art/community-web/v1/model/detail"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
        "Content-Type": "application/json"
    }

    params = {"modelId": model_id}

    with httpx.Client() as client:
        client.headers.update(headers)
        r = client.get(url, params=params)
    
    response_data = r.json()

    return response_data

