import re
import json
import pathlib
from html.parser import HTMLParser
from typing import Literal
from typing import Iterable

import httpx

from . import util
from .civitai_constants import GenTag
from .civitai_constants import Tool
from .civitai_constants import Technique
from .civitai_constants import Sort
from .civitai_constants import Period
from .civitai_constants import ModelSort
from .civitai_constants import ModelType
from .civitai_constants import BaseModel
from .civitai_constants import FileFormat
from .civitai_constants import CheckpointType

_BrowsingLevel = int


def to_json(data):
    return json.dumps(data, separators=(",", ":"))


class civitai:
    base_trpc = "https://civitai.com/api/trpc"
    _public_image_key = "xG1nkqKTMzGDvpLrqFT7WA"

    def __init__(self, api_key:str=None, browsing_level:list[_BrowsingLevel]=None, **kwargs):
        self.api_key = api_key
        
        self.account_settings = kwargs.get("account_settings")

        if self.api_key and not self.account_settings:
            self.account_settings: dict | None = self.get_account_settings()

        if browsing_level == None:
            if self.account_settings:
                self.set_browsing_level(self.account_settings["browsingLevel"])
            else:
                self.set_browsing_level("PG")
        else:
            self.set_browsing_level(*browsing_level)
    

    @classmethod
    def preload(cls, api_key:str, browsing_level:int, account_settings:dict):
        isinstance = cls(api_key, browsing_level, account_settings=account_settings)


    def me(self):
        """
        Get user id information (REQUIRES API KEY)
        """
        
        with httpx.Client(headers=self.auth_headers()) as client:
            r = client.get("https://civitai.com/api/v1/me")

            jsondata = r.json()

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
            

    def get_generation_queue(self, cursor:str=None, asc:bool=False, tags:list[GenTag]=None):
        url = self.base_trpc + "/orchestrator.queryGeneratedImages"
        
        tags_modified = []
        if tags and len(tags) > 0:
            for tag in tags:
                if isinstance(tag, GenTag):
                    tags_modified.append(tag.value)
                elif tag in (GenTag._member_map_.keys()):
                    tags_modified.append(GenTag._member_map_[tag].value)
                elif tag in (GenTag._member_map_.values()):
                    tags_modified.append(tag)


        query_data = {
            "ascending": asc,
            "tags": tags_modified,
            "authed": True,
        }

        if cursor:
            query_data["json"]["cursor"] = cursor

        input_json = to_json({"json": query_data})

        params = {"input": input_json}

        headers = self.auth_headers()

        with httpx.Client(headers=headers) as client:
            req = client.build_request("GET", url, params=params)
            
            r = client.send(req)

            jsondata = r.json()
            jsondata = jsondata.get("result", {}).get("data", {}).get("json", {})

            return jsondata


    def get_all_generations(self, asc:bool=False, tags:list[GenTag]=None):
        url = self.base_trpc + "/orchestrator.queryGeneratedImages"
        
        headers = self.auth_headers()

        tags_modified = []
        if tags and len(tags) > 0:
            for tag in tags:
                if isinstance(tag, GenTag):
                    tags_modified.append(tag.value)
                elif tag in (GenTag._member_map_.keys()):
                    tags_modified.append(GenTag._member_map_[tag].value)
                elif tag in (GenTag._member_map_.values()):
                    tags_modified.append(tag)
        
        def get_queue_with_cursor(client: httpx.Client, cursor:str=None, asc:bool=False, tags:list[GenTag]=None):
            _input_json = {
                "ascending": asc,
                "tags": tags,
                "authed": True
            }
            if cursor:
                _input_json["cursor"] = cursor
            
            _params = {"input": to_json({"json": _input_json})}
            
            req = client.build_request("GET", url, params=_params)
            
            r = client.send(req)

            jsondata = r.json()
            jsondata = jsondata.get("result", {}).get("data", {}).get("json", {})

            return jsondata

        all_items = []
        
        with httpx.Client(headers=headers) as client:
            data = get_queue_with_cursor(client, cursor=None, asc=asc, tags=tags_modified)
            all_items.extend(data.get("items", []))
            cursor = data.get("nextCursor")
            while cursor != None:
                data = get_queue_with_cursor(client, cursor)
                all_items.extend(data.get("items", []))
                cursor = data.get("nextCursor")
                print(cursor)
        
        return all_items


    def get_image_generation_data(self, image_id:int, **kwargs):
        """
        Get metadata for a published generated image
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
            sort_by:Sort=None,
            period:Period=None,
            types:list[Literal["image", "video"]]=None,
            tools:list[Tool]=None,
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


        if sort_by:
            if isinstance(sort_by, Sort):
                sort_by = sort_by.value
            elif sort_by in (Sort._member_map_.keys()):
                sort_by = Sort._member_map_[sort_by].value
            elif sort_by in Sort._member_map_.values():
                pass
            else:
                sort_by = Sort.NEWEST.value
        else:
            sort_by = Sort.NEWEST.value

        if period:
            if isinstance(period, Period):
                period = period.value
            elif period in (Period._member_map_.keys()):
                period = Period._member_map_[sort_by].value
            elif period in Period._member_map_.values():
                pass
            else:
                period = Period.ALLTIME.value
        else:
            period = Period.ALLTIME.value

        tools_modified = []
        if tools and len(tools) > 0:
            for tool in tools:
                if isinstance(tool, Tool):
                    tools_modified.append(tool.id)
                elif tool in Tool._member_map_.keys():
                    tools_modified.append(Tool._member_map_[tool].id)
                elif tool in [x.value[0] for x in Tool._member_map_.values()]:
                    for t in Tool._member_map_.values():
                        if t.value[0] == tool:
                            tools_modified.append(t.value[1])
                            break
                elif tool in [x.value[1] for x in Tool._member_map_.values()]:
                    tools_modified.append(tool)

        techniques_modified = []
        if techniques and len(techniques) > 0:
            for technique in techniques:
                if isinstance(technique, Technique):
                    techniques_modified.append(technique.id)
                elif technique in Technique._member_map_.keys():
                    techniques_modified.append(Technique._member_map_[technique].id)
                elif technique in [x.value[0] for x in Technique._member_map_.values()]:
                    for t in Technique._member_map_.values():
                        if t.value[0] == technique:
                            techniques_modified.append(t.value[1])
                            break
                elif technique in [x.value[1] for x in Technique._member_map_.values()]:
                    techniques_modified.append(technique)

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

        if len(tools_modified) > 0:
            query_data["tools"] = tools_modified

        if base_models:
            if isinstance(base_models, str):
                base_models = [base_models]
            query_data["baseModels"] = base_models
        
        if made_onsite != None:
            query_data["fromPlatform"] = made_onsite

        if remixes_only != None:
            query_data["remixesOnly"] = remixes_only
            query_data["nonRemixesOnly"] = not remixes_only
        
        if len(techniques_modified) > 0:
            query_data["techniques"] = techniques_modified

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


    def get_user_models(self, username:str, sort_by:ModelSort=None, period:Period=None, early_access:bool=None, onsite_generation:bool=None, made_onsite:bool=None, cursor:str=None):
        url = self.base_trpc + "/model.getAll"

        early_access = False if early_access == None else early_access
        onsite_generation = False if early_access == None else onsite_generation
        made_onsite = False if early_access == None else made_onsite


        if sort_by:
            if isinstance(sort_by, ModelSort):
                sort_by = sort_by.value
            elif sort_by in (ModelSort._member_map_.keys()):
                sort_by = ModelSort._member_map_[sort_by].value
            elif sort_by in ModelSort._member_map_.values():
                pass
            else:
                sort_by = ModelSort.NEWEST.value
        else:
            sort_by = ModelSort.NEWEST.value


        if period:
            if isinstance(period, Period):
                period = period.value
            elif period in (Period._member_map_.keys()):
                period = Period._member_map_[sort_by].value
            elif period in Period._member_map_.values():
                pass
            else:
                period = Period.ALLTIME.value
        else:
            period = Period.ALLTIME.value


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

        if self.username and not username:
            username = self.username

        browsing_level = self.browsing_level

        sort_by = "Newest" if sort_by == None else sort_by
        period = "AllTime" if period == None else period

        input_json = {
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
            "authed": True,
        }

        if cursor:
            input_json["json"]["cursor"] = cursor

        input_json = to_json({"json": input_json})

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


    def get_post(self, post_id:str):
        url = f"https://civitai.com/api/v1/images?postId={post_id}"
        
        with httpx.Client() as client:
            r = client.get(url)

            jsondata = r.json()

            return jsondata


    def get_tools(self, from_api:bool=False):
        """Get list of all tools"""
        if from_api == True:
            url = self.base_trpc + "/tool.getAll"

            query_data = {
                "include": ["unlisted"],
                "sort": "AZ",
                # "cursor": None,
                "authed": True
            }

            input_json = to_json({"json": query_data})
            params = {"input": input_json}

            with httpx.Client() as client:
                req = client.build_request("GET", url, params=params)

                r = client.send(req)
                
                jsondata = r.json().get("result", {}).get("data", {}).get("json", {}).get("items", [])

                return jsondata
        else:
            with pathlib.Path(__file__).parent.joinpath("tools.json").open("r") as fp:
                return json.load(fp)


    def get_model(self, model_id):
        url = f"https://civitai.com/api/v1/models/{model_id}"
        
        with httpx.Client(headers=self.auth_headers()) as client:
            r = client.get(url)
            
            jsondata = r.json()

            return jsondata
    

    def get_model_version(self, model_version_id):
        url = f"https://civitai.com/api/v1/model-versions/{model_version_id}"
        
        with httpx.Client(headers=self.auth_headers()) as client:
            r = client.get(url)
            
            jsondata = r.json()

            return jsondata
    

    def get_model_version_by_hash(self, hash_value):
        url = f"https://civitai.com/api/v1/model-versions/by-hash/{hash_value}"
        
        with httpx.Client(headers=self.auth_headers()) as client:
            r = client.get(url)
            
            jsondata = r.json()

            return jsondata

    
    def get_model_alt(self, model_id):
        with httpx.Client(headers=self.auth_headers()) as client:
            query_data = {"id": int(model_id), "authed": True}
            
            params = {"input": to_json({"json": query_data})}
            
            url = self.base_trpc + "/model.getById"
            
            r = client.get(url, params=params)

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
    def user_id(self):
        if self.account_settings:
            return self.account_settings["id"]
        
    @property
    def username(self):
        if self.account_settings:
            return self.account_settings["username"]

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

    
    @staticmethod
    def parse_air(string:str):
        m = re.search(
            r"^(?:urn:)?(?:air:)?(?:([a-zA-Z0-9_\-\/]+):)?(?:([a-zA-Z0-9_\-\/]+):)?([a-zA-Z0-9_\-\/]+):([a-zA-Z0-9_\-\/]+)(?:@([a-zA-Z0-9_\-]+))?(?:\.([a-zA-Z0-9_\-]+))?$", 
            string
        )

        if m:
            airdict = {"ecosystem": None, "type": None, "source": None, "id": None, "version": None, "format": None}
            groups = m.groups()
            
            import rich
            rich.print(len(groups))
            rich.print(groups)
            if len(groups) == 6:
                airdict["ecosystem"], airdict["type"], airdict["source"], airdict["id"], airdict["version"], airdict["format"] = m.groups()
            elif len(groups) == 5:
                airdict["ecosystem"], airdict["type"], airdict["source"], airdict["id"], airdict["version"] = m.groups()
            
            return airdict


    @staticmethod
    def to_air_string(_ecosystem:str=None, _type:str=None, _source:str=None, _id=None, _version=None, _format=None) -> str:
        if isinstance(_ecosystem, dict):
            data = _ecosystem
            _ecosystem = data["ecosystem"]
            _type = data["type"]
            _source = data["source"]
            _id = data["id"]
            _version = data["version"]
            _format = data["format"]

        string = "urn:air:{}:{}:{}:{}@{}".format(
            _ecosystem, _type, _source, _id, _version
        )

        if _format:
            string += f".{_format}"
        
        return string

        


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




def model_lookup(model_id):
    url = f"https://civitai.com/api/v1/models/{model_id}"
    r = httpx.get(url)
    jsondata = r.json()
    return jsondata


def model_version_lookup(model_version_id):
    url = f"https://civitai.com/api/v1/model-versions/{model_version_id}"
    r = httpx.get(url)
    jsondata = r.json()
    return jsondata


def bulk_resource_lookup(model_version_ids:list):
    reqlist = []
    
    for mvid in model_version_ids:
        url = f"https://civitai.com/api/v1/model-versions/{mvid}"
        req = httpx.Request("GET", url)
        reqlist.append(req)

    responses = util.fetch_bulk(reqlist)

    json_responses = [r.json() for r in responses]

    return json_responses

