import json
import asyncio
from html.parser import HTMLParser
from typing import Literal
from typing import Iterable

import httpx
import rich.logging

from . import util

_BrowsingLevel = int



def to_json(data):
    return json.dumps(data, separators=(",", ":"))


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

class Technique:
    TXT2IMG = 1
    IMG2IMG = 2
    INPAINTING = 3
    WORKFLOW = 4
    VID2VID = 5
    TXT2VID = 6
    IMG2VID = 7
    CONTROLNET = 8

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
    

    def get_generation_queue(self, cursor:str=None, asc:bool=False, tags:list[str]=None):
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


    def get_image_generation_data(self, image_id:int, **kwargs):
        """
        """
        
        url = self.base_trpc + "/image.getGenerationData"

        query_data = {"id": image_id, "authed":True}

        input_json = to_json({"json": query_data})

        params = {"input": input_json}

        with httpx.Client() as client:
            req = client.build_request("GET", url, params=params)

            r = client.send(req)

            jsondata = r.json().get("result", {}).get("data", {}).get("json", {})

            return jsondata


    def get_images(
            self, 
            cursor=None, 
            sort_by=None,
            period=None,
            types:list[Literal["image", "video"]]=None,
            tools:list=None,
            base_models:list=None, 
            made_onsite:bool=None, 
            remixes_only:bool=None, 
            techniques:list=None, 
            has_metadata:bool=None, 
            followed:bool=None, 
            hidden:bool=None, 
            **kwargs
        ):
        """
        Fetch and query the image feed on CivitAI
        """
        
        url = self.base_trpc + "/image.getInfinite"

        sort_by = "Newest" if sort_by == None else sort_by
        period = "AllTime" if period == None else period

        query_data = {
            "period": period, 
            "sort": sort_by, 
            "withMeta": False,
            "fromPlatform": False,
            "hideAutoResources": False,
            "hideManualResources": False, 
            "hidden": False,
            "notPublished": False, 
            "scheduled": False, 
            "remixesOnly": False,
            # "nonRemixesOnly": True, 
            "useIndex": True, 
            "browsingLevel": self.browsing_level, 
            "include": ["cosmetics"],
            "authed": True,
        }

        if types:
            if isinstance(types, str):
                types = [types]
            types = [_type.lower() for _type in types]
            query_data["types"] = types

        if cursor:
            query_data["cursor"] = cursor

        if base_models:
            if isinstance(base_models, str):
                base_models = [base_models]
            query_data["baseModels"] = base_models
        
        if made_onsite != None:
            query_data["fromPlatform"] = made_onsite

        if remixes_only != None:
            query_data["remixesOnly"] = remixes_only
            query_data["nonRemixesOnly"] = not remixes_only
        
        if techniques:
            technique_map = {"txt2img": 1, "img2img": 2, "inpainting": 3, "workflow": 4, "vid2vid": 5, "txt2vid": 6, "img2vid": 7, "controlnet": 8}
            query_data["techniques"] = []
            for t in techniques:
                if isinstance(t, int):
                    query_data["techniques"].append(t)
                elif isinstance(t, str):
                    query_data["techniques"].append(technique_map[t.lower()])

        if has_metadata != None:
            query_data["withMeta"] = has_metadata
            
        if followed != None:
            query_data["followed"] = followed
        
        if hidden != None:
            query_data["hidden"] = hidden

        input_json = to_json({"json": query_data})
        params = {"input": input_json}

        with httpx.Client(headers=self.auth_headers()) as client:
            req = client.build_request("GET", url, params=params)

            r = client.send(req)
            
            jsondata = r.json().get("result", {}).get("data", {}).get("json", {})

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
                "browsingLevel": self.browsing_level,
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

        browsing_level = self.browsing_level

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


    def get_user_images(self, username:str=None, sort_by:str=None, period:str=None, cursor:str=None, section: Literal["published","draft"]="published"):
        """
        Fetch and query images for a specific user. If no user is specified, 
        defaults to the account that the api key belongs to (if one was provided)
        """
        url = self.base_trpc + "/image.getInfinite"

        if not username:
            username = self.account_settings["username"]

        browsing_level = self.browsing_level

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
    def browsing_level(self):
        return self.__browsing_level
    

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
            self.__browsing_level = civitai._generate_browsing_level_bit_values(*args)
        else:
            raise ValueError("Browsing level value required: ('PG', 'PG13', 'R', 'X', 'XXX')")


    def get_browsing_level_keys(self) -> list[str]:
        return civitai._get_levels_from_bit_value(self.browsing_level)

    
    def auth_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}


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

