import re
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