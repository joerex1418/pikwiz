import json
import asyncio
from html.parser import HTMLParser
from typing import Literal
from typing import Iterable

import httpx
import rich.logging

from . import util

_BrowsingLevel = int


def _get_levels_from_bit_value(value: int) -> list[str]:
    content_flags = {
        "PG": 1,
        "PG13": 2,
        "R": 4,
        "X": 8,
        "XXX": 16
    }

    result = []  # List to store matching levels
    
    for level, bit in content_flags.items():
        if value & bit:  # Check if the bit is set in the given value
            result.append(level)  # Add the corresponding level to the list
    
    return result


class ModelSort:
    NEWEST = "Newest"
    OLDEST = "Oldest"
    HIGHEST_RATED = "Highest Rated"
    MOST_LIKED = "Most Liked"
    MOST_COLLECTED = "Most Collected"
    MOST_DOWNLOADED = "Most Downloaded"
    MOST_DISCUSSED = "Most Discussed"
    MOST_IMAGES = "Most Images"

class PostSort:
    NEWEST = "Newest"
    OLDEST = "Oldest"
    MOST_REACTIONS = "Most Reactions"
    MOST_COMMENTS = "Most Comments"
    MOST_COLLECTED = "Most Collected"

class Tag:
    GEN = "gen"
    IMG = "img"
    TXT2IMG = "txt2img"
    LIKED = "feedback:liked"
    DISLIKED = "feedback:disliked"
    FAVORITED = "favorite"

class Period:
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"
    YEAR = "Year"
    ALLTIME = "AllTime"

class ModelType:
    CHECKPOINT = "Checkpoint"
    TEXTUALINVERSION = "TextualInversion"
    HYPERNETWORK = "Hypernetwork"
    AESTHETICGRADIENT = "AestheticGradient"
    LORA = "LORA"
    LOCON = "LoCon"
    DORA = "DoRA"
    CONTROLNET = "Controlnet"
    UPSCALER = "Upscaler"
    MOTIONMODULE = "MotionModule"
    VAE = "VAE"
    POSES = "Poses"
    WILDCARDS = "Wildcards"
    WORKFLOWS = "Workflows"
    DETECTION = "Detection"
    OTHER = "Other"

class CheckpointType:
    ALL = "all"
    TRAINED = "Trained"
    MERGE = "Merge"

class FileFormat:
    SAFETENSOR = "SafeTensor"
    PICKLETENSOR = "PickleTensor"
    GGUF = "GGUF"
    DIFFUSERS = "Diffusers"
    CORE_ML = "Core ML"
    ONNX = "ONNX"

class BaseModel:
    SD_1_4 = "SD 1.4"
    SD_1_5 = "SD 1.5"
    SD_1_5_LCM = "SD 1.5 LCM"
    SD_1_5_HYPER = "SD 1.5 Hyper"
    SD_2_0 = "SD 2.0"
    SD_2_1 = "SD 2.1"
    SDXL_1_0 = "SDXL 1.0"
    SD_3 = "SD 3"
    SD_3_5 = "SD 3.5"
    SD_3_5_MEDIUM = "SD 3.5 Medium"
    SD_3_5_LARGE = "SD 3.5 Large"
    SD_3_5_LARGE_TURBO = "SD 3.5 Large Turbo"
    PONY = "Pony"
    FLUX_1_S = "Flux.1 S"
    FLUX_1_D = "Flux.1 D"
    AURAFLOW = "AuraFlow"
    SDXL_LIGHTNING = "SDXL Lightning"
    SDXL_HYPER = "SDXL Hyper"
    SVD = "SVD"
    PIXART_A = "PixArt a"
    PIXART_E = "PixArt E"
    HUNYUAN_1 = "Hunyuan 1"
    HUNYUAN_VIDEO = "Hunyuan Video"
    LUMINA = "Lumina"
    KOLORS = "Kolors"
    ILLUSTRIOUS = "Illustrious"
    MOCHI = "Mochi"
    LTXV = "LTXV"
    COGVIDEOX = "CogVideoX"
    OTHER = "Other"


class civitai:
    base_trpc = "https://civitai.com/api/trpc"
    _public_image_key = "xG1nkqKTMzGDvpLrqFT7WA"

    def __init__(self, api_key:str=None, default_browsing_level:list[_BrowsingLevel]=None):
        self.api_key = api_key
        
        self.account_settings = None
        if self.api_key:
            self.account_settings: dict | None = self.get_account_settings()

        if default_browsing_level == None:
            if self.account_settings:
                self.set_browsing_level(self.account_settings["browsingLevel"])
            else:
                self.set_browsing_level("PG")
        else:
            self.set_browsing_level(*default_browsing_level)
    

    def get_generated_images(self, cursor:str=None, asc:bool=False, tags:list[str]=None):
        url = self.base_trpc + "/orchestrator.queryGeneratedImages"
        
        tags = [] if tags == None else tags
        
        input_json = {
            "json": {
                "ascending": asc,
                "tags": tags,
                "authed": True
            }
        }

        if cursor:
            input_json["json"]["cursor"] = cursor

        input_json = json.dumps(input_json, separators=(",", ":"))

        params = {"input": input_json}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(headers=headers) as client:
            req = client.build_request("GET", url, params=params)
            
            r = client.send(req)

            jsondata = r.json()

            return jsondata


    def get_user(self, username:str):
        url = self.base_trpc + "/user.getCreator"
        
        input_json = {
            "json": {
                "username": username,
                "authed": True
            },
        }

        input_json = json.dumps(input_json, separators=(",", ":"))

        params = {"input": input_json}

        # headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client() as client:
            req = client.build_request("GET", url, params=params)
            
            r = client.send(req)

            jsondata = r.json()

            return jsondata


    def get_user_models(self, username:str, sort_by:str=None, period:str=None, early_access:bool=None, onsite_generation:bool=None, made_onsite:bool=None, cursor:str=None):
        url = self.base_trpc + "/model.getAll"

        browsing_level = self.default_browsing_level

        sort_by = "Newest" if sort_by == None else sort_by
        period = "AllTime" if period == None else period
        early_access = False if early_access == None else early_access
        onsite_generation = False if early_access == None else onsite_generation
        made_onsite = False if early_access == None else made_onsite

        input_json = {
            "json": {
                "username": username,
                "sort": sort_by, 
                "period": period, 
                "pending": False, 
                "hidden": False, 
                "followed": False, 
                "earlyAccess": early_access, 
                "fromPlatform": made_onsite, 
                "supportsGeneration": onsite_generation,
                # "limit": 5,
                "browsingLevel": browsing_level,
                "authed": True
            }
        }

        if cursor:
            input_json["json"]["cursor"] = cursor

        input_json = json.dumps(input_json, separators=(",", ":"))

        params = {"input": input_json}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(headers=headers, timeout=httpx.Timeout(10)) as client:
            req = client.build_request("GET", url, params=params)
            
            r = client.send(req)

            jsondata = r.json().get("result", {}).get("data", {}).get("json", {})

            return jsondata


    def get_user_posts(self, username:str, sort_by:str=None, period:str=None, cursor:str=None, section: Literal["published","draft"]="published"):
        url = self.base_trpc + "/post.getInfinite"

        browsing_level = self.default_browsing_level

        sort_by = "Newest" if sort_by == None else sort_by
        period = "AllTime" if period == None else period

        draft_only = True if section == "draft" else False

        input_json = {
            "json": {
                "browsingLevel": browsing_level,
                "period": period, 
                "periodMode": "published",
                "sort": sort_by, 
                "username": username,
                "section": section,
                "followed": False, 
                "draftOnly": draft_only,
                "pending": True, 
                "include": ["cosmetics"],
                "authed": True,
            },
        }

        if cursor:
            input_json["json"]["cursor"] = cursor

        input_json = json.dumps(input_json, separators=(",", ":"))

        params = {"input": input_json}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(headers=headers, timeout=httpx.Timeout(10)) as client:
            req = client.build_request("GET", url, params=params)
            
            r = client.send(req)

            jsondata = r.json().get("result", {}).get("data", {}).get("json", {})

            for item in jsondata.get("items", []):
                for image in item.get("images", []):
                    image["fullUrl"] = civitai._create_image_url(image["url"])

            return jsondata


    # This was dumb. I don't think this is helpful at all
    async def _async_get_account_posts(self, username, sort_by, period, cursor, section):
        url = self.base_trpc + "/post.getInfinite"

        browsing_level = self.default_browsing_level

        sort_by = "Newest" if sort_by == None else sort_by
        period = "AllTime" if period == None else period

        draft_only = True if section == "draft" else False

        input_json = {
            "json": {
                "browsingLevel": browsing_level,
                "period": period, 
                "periodMode": "published",
                "sort": sort_by,
                "username": username,
                "section": section,
                "followed": False, 
                "draftOnly": draft_only,
                "pending": True, 
                "include": ["cosmetics"],
                "authed": True,
            },
        }

        if cursor:
            input_json["json"]["cursor"] = cursor

        input_json = json.dumps(input_json, separators=(",", ":"))

        params = {"input": input_json}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(10)) as client:
            req = client.build_request("GET", url, params=params)

            r = await client.send(req)

            jsondata = r.json().get("result", {}).get("data", {}).get("json", {})

            for item in jsondata.get("items", []):
                for image in item.get("images", []):
                    image["fullUrl"] = civitai._create_image_url(image["url"])

            return jsondata


    def get_account_posts(self, username:str, sort_by:str=None, period:str=None, cursor:str=None, section: Literal["published","draft"]="published"):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            return asyncio.ensure_future(self._async_get_account_posts(username, sort_by, period, cursor, section))
        else:
            return asyncio.run(self._async_get_account_posts(username, sort_by, period, cursor, section))


    def get_user_images(self, username:str, sort_by:str=None, period:str=None, cursor:str=None):
        url = self.base_trpc + "/image.getInfinite"

        browsing_level = self.default_browsing_level

        sort_by = "Newest" if sort_by == None else sort_by
        period = "AllTime" if period == None else period

        input_json = {
            "json": {
                "period": period,
                "sort": sort_by,
                "types":["image"],
                "withMeta": False, 
                "fromPlatform": False, 
                "hideAutoResources": False, 
                "hideManualResources": False, 
                "notPublished": False, 
                "scheduled": False, 
                "nonRemixesOnly": False, 
                "username": username, 
                "useIndex": True, 
                "browsingLevel": browsing_level, 
                "include": ["cosmetics"], 
                "authed": True
            }
        }

        if cursor:
            input_json["json"]["cursor"] = cursor

        input_json = json.dumps(input_json, separators=(",", ":"))

        params = {"input": input_json}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(headers=headers, timeout=httpx.Timeout(10)) as client:
            req = client.build_request("GET", url, params=params)
            
            r = client.send(req)

            jsondata = r.json().get("result", {}).get("data", {}).get("json", {})

            for image_item in jsondata.get("items", []):
                image_item["fullUrl"] = civitai._create_image_url(image_item["url"])

            return jsondata


    def get_user_hidden_settings(self):
        url = self.base_trpc + "/hiddenPreferences.getHidden"

        input_json = {"json": {"authed": True}}

        input_json = json.dumps(input_json, separators=(",", ":"))

        headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(headers=headers) as client:
            req = client.build_request("GET", url)
            
            r = client.send(req)

            jsondata = r.json().get("result", {}).get("data", {}).get("json", {})

            return jsondata


    def get_account_settings(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(headers=headers) as client:
            req = client.build_request("GET", "https://civitai.com/user/account")
            
            r = client.send(req)

            parser = _ScriptTagParser()
            parser.feed(r.text)

            jsondata = json.loads(parser.script_tag_text.strip())
            page_props = jsondata.get("props", {}).get("pageProps", {})
            userdata = page_props.get("session", {}).get("user", {})
            settings = page_props.get("settings", {})

            return userdata


    def get_account_buzz(self):
        url = self.base_trpc + "/buzz.getBuzzAccount"
        
        input_json = {
            "json": {
                "accountId": self.account_settings["id"],
                "accountType": None,
                "authed": True,
            }
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(headers=headers) as client:
            reqlist = []
            for account_type in ("user", "generation"):
                input_json["json"]["accountType"] = account_type
                params = {"input": json.dumps(input_json, separators=(",", ":"))}
                req = client.build_request("GET", url, params=params)
                reqlist.append(req)
            
            responses = util.fetch_bulk(reqlist)
            json_responses = []
            for r in responses:
                rjson = r.json().get("result", {}).get("data", {}).get("json", {})
                if "generation" in r.url.__str__().lower():
                    rjson["account_type"] = "generation"
                else:
                    rjson["account_type"] = "user"
                
                json_responses.append(rjson)
                    
            return json_responses
            

    def get_post(self, post_id:str):
        url = f"https://civitai.com/api/v1/images?postId={post_id}"
        
        with httpx.Client() as client:
            r = client.get(url)

            jsondata = r.json()

            return jsondata


    @staticmethod
    def _create_image_url(image_uuid:str, width:int=None):
        if width == None:
            return f"https://image.civitai.com/{civitai._public_image_key}/{image_uuid}/original=true"
        else:
            return f"https://image.civitai.com/{civitai._public_image_key}/{image_uuid}/width={width}"
    

    @staticmethod
    def _generate_browsing_level_bit_values(*levels:Literal["PG", "PG13", "R", "X", "XXX"]):
        content_flags = {
            "PG": 1,
            "PG13": 2,
            "R": 4,
            "X": 8,
            "XXX": 16
        }
        
        result = 0

        for level in levels:
            if isinstance(level, int) and level not in (content_flags.values()):
                return level
            elif level in content_flags.values():
                result |= result
            elif str(level).upper() in content_flags.keys():
                result |= content_flags[level]
        
        if result == 0:
            result = 1 # PG

        return result


    @staticmethod
    def _get_levels_from_bit_value(value: int) -> list[str]:
        content_flags = {
            "PG": 1,
            "PG13": 2,
            "R": 4,
            "X": 8,
            "XXX": 16
        }

        result = []  # List to store matching levels
        
        for level, bit in content_flags.items():
            if value & bit:  # Check if the bit is set in the given value
                result.append(level)  # Add the corresponding level to the list
        
        return result


    @property
    def default_browsing_level(self):
        return self.__default_browsing_level
    

    def set_browsing_level(self, *args:_BrowsingLevel):
        """
        NOTE: Only sets browsing level within this python class. 
        This will not set the browsing for your CivitAI account
        """
        if len(args) > 0:
            if isinstance(args[0], Iterable) and not isinstance(args[0], (str, bytes, bytearray, int)):
                args = args[0]
            elif isinstance(args[0], int) or isinstance(args[0], str):
                ...
            self.__default_browsing_level = civitai._generate_browsing_level_bit_values(*args)
        else:
            raise ValueError("Browsing level value required: ('PG', 'PG13', 'R', 'X', 'XXX')")


    def get_browsing_level_keys(self) -> list[str]:
        return civitai._get_levels_from_bit_value(self.default_browsing_level)




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



async def _fetch_one(client:httpx.AsyncClient, url:str):
    r = await client.get(url)
    return r

async def _fetch_all(urllist:list, **kwargs):
    async with httpx.AsyncClient() as session:
        tasks = (asyncio.create_task(_fetch_one(session, url)) for url in urllist)
        responses = await asyncio.gather(*tasks)
        return responses

def fetch_all(urllist:list, **kwargs):
    if isinstance(urllist,str):
        urllist = [urllist]
    return asyncio.run(_fetch_all(urllist, **kwargs))



def model_lookup(model_id):
    url = f"https://civitai.com/api/v1/models/{model_id}"
    r = httpx.get(url)
    return r.json()

def model_version_lookup(model_version_id):
    url = f"https://civitai.com/api/v1/model-versions/{model_version_id}"
    r = httpx.get(url)
    return r.json()


def bulk_resource_lookup(model_version_ids:list):
    urllist = []
    
    for mvid in model_version_ids:
        urllist.append(f"https://civitai.com/api/v1/model-versions/{mvid}")

    responses = fetch_all(urllist)

    json_responses = [r.json() for r in responses]

    return json_responses

