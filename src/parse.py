import io
import re
import json
from pathlib import Path

import rich
import httpx
from PIL import Image
from PIL.ExifTags import TAGS

from .color import color
from .color import cprint
from .color import console as console
from .civitai_api import civitai
from .civitai_constants import SAMPLER_MAP
from .civitai_constants import CIVITAI_SAMPLER_DROPDOWN_MAP
from .prompt import parse_weighted_prompt_tags

class ImageData:
    def __init__(self, data: str | io.BytesIO | Image.Image):
        if isinstance(data, Image.Image):
            self.image = data

        elif isinstance(data, (str, Path)):
            data = Path(data).resolve()

            with Image.open(data) as image:
                self.image = image
        
        elif isinstance(data, io.BytesIO):
            with Image.open(data) as image:
                self.image = image

        # self.raw_prompt = self._get_raw_prompt()
        self.raw_prompt = extract_prompt_from_image(self.image)


    def _get_raw_prompt_old(self) -> str | None:
        if self.image.format in ("PNG", "WEBP"):
            prompt_str = self.image.info["parameters"]
        
        elif self.image.format in ("JPEG", "JPG", "TIFF", "JFIF"):
            try:
                exif_data = self.image._getexif()
            except:
                exif_data = self.image.getexif()
            
            if exif_data:
                exif_dict = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
                if "UserComment" in exif_dict:
                    raw_comment: bytes = exif_dict["UserComment"]
                    if raw_comment.startswith(b"UNICODE"):
                        prompt_str = raw_comment[7:].decode("utf-8")
        else:
            prompt_str = ""
        
        return prompt_str.replace("\x00", "")



def extract_prompt_from_image(image: Image.Image):
    prompt_str = ""
    
    if "parameters" in image.info.keys():
        prompt_str = image.info["parameters"]
    
    else:
        try:
            exif_data = image._getexif()
            if exif_data:
                exif_dict = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
                if "UserComment" in exif_dict:
                    raw_comment: bytes = exif_dict["UserComment"]
                    if b"UNICODE" in raw_comment:
                        prompt_str = raw_comment[raw_comment.find(b"UNICODE") + 7:].decode("utf-8")
                    elif b"ASCII" in raw_comment:
                        prompt_str = raw_comment[raw_comment.find(b"ASCII") + 5:].decode("utf-8")
                    else:
                        cprint.bright_red("Couldn't find data in UserComment")

        except:
            exif_bytes: bytes = image.info["exif"]

            if b"UNICODE" in exif_bytes:
                prompt_str = exif_bytes[exif_bytes.find(b"UNICODE") + 7:].decode("utf-8")
            else:
                cprint.bright_red("Couldn't find data in exif byte string")

    
    return prompt_str.replace("\x00", "")


def parse_prompt_string(raw_prompt_string):
    json_data = None
    extra_metadata = None
    
    try:
        json_data = json.loads(raw_prompt_string)
    except json.JSONDecodeError as e:
        cprint.yellow("Not raw JSON string")
    
    if json_data:
        # ==================================== #
        # CivitAI on-site img2img gen
        # ==================================== #
        extra_metadata = json.loads(json_data["extraMetadata"])
        console.print_json(data=extra_metadata)
        
        prompts = "{} \nNegative prompt: {}\n".format(extra_metadata["prompt"], extra_metadata["negativePrompt"])
        
        settings = "Steps: {steps}, CFG Scale: {cfgscale}, Sampler: {sampler}, Schedule type: {scheduler}, workflowId: {workflowid}, civitai resources: {civitai_resources}".format(
            steps = extra_metadata["steps"],
            cfgscale = extra_metadata["cfgScale"],
            sampler = CIVITAI_SAMPLER_DROPDOWN_MAP.get(extra_metadata["sampler"], ['', ''])[0],
            scheduler = CIVITAI_SAMPLER_DROPDOWN_MAP.get(extra_metadata["sampler"], ['', ''])[1],
            workflowid = extra_metadata["workflowId"],
            civitai_resources = json.dumps(extra_metadata["resources"])
        )
    else:
        match = re.search(r"(?P<prompts>.*?)(?P<settings>steps:.*)", raw_prompt_string, re.DOTALL | re.IGNORECASE)
        prompts = match.groupdict()["prompts"]
        settings = match.groupdict()["settings"]
    
    # ==================================== #
    # CivitAI on-site img2img gen
    # ==================================== #
    # try:
    #     assert(match)
    #     prompts = match.groupdict()["prompts"]
    #     settings = match.groupdict()["settings"]
    # except AssertionError as e:
    #     # console.print_json(raw_prompt_string)
    #     # raise AssertionError(e)
    #     try:
    #         json_data = json.loads(raw_prompt_string)
    #     except json.JSONDecodeError as e:
    #         raise e

    # --------------------------------------- #
    # Prompt strings
    # --------------------------------------- #
    match = re.search(r"^(?P<pos>.*?)(?:\bnegative prompt:\s*(?P<neg>.*))?$", prompts, re.DOTALL | re.IGNORECASE)
    # try:
    #     match = re.search(r"^(?P<pos>.*?)(?:\bnegative prompt:\s*(?P<neg>.*))?$", prompts, re.DOTALL | re.IGNORECASE)
    # except:
    #     match = None

    positive_prompt = match.groupdict()["pos"]
    negative_prompt = match.groupdict()["neg"]

    # ==================================== #
    # CivitAI on-site img2img gen
    # ==================================== #
    # if match:
    #     positive_prompt = match.groupdict()["pos"]
    #     negative_prompt = match.groupdict()["neg"]
    # else:
    #     assert("extraMetadata" in json_data)

    #     _extrametadata = json.loads(json_data["extraMetadata"])
    #     console.print_json(data=_extrametadata)
    #     positive_prompt = _extrametadata["prompt"]
    #     negative_prompt = json_data["negativePrompt"]

    if isinstance(positive_prompt, str):
        positive_prompt = positive_prompt.strip().strip(",").strip()
    if isinstance(negative_prompt, str):
        negative_prompt = negative_prompt.strip().strip(",").strip()

    # --------------------------------------- #
    # Read LoRA and Embedding data
    # --------------------------------------- #
    lora_weights = re.findall(r"<lora:(?P<name>.*?):?(?P<weight>\d+|\d+\.\d+)?>", positive_prompt, re.DOTALL | re.IGNORECASE)
    embed_weights = re.findall(r"<embed:(?P<name>.*?):?(?P<weight>\d+|\d+\.\d+)?>", positive_prompt, re.DOTALL | re.IGNORECASE)
    lora_weights = [[x[0], float(x[1])] for x in lora_weights]
    embed_weights = [[x[0], float(x[1])] for x in embed_weights]

    # --------------------------------------- #
    # Get Weighted Prompt Tags
    # --------------------------------------- #
    positive_prompt_weight_tags = parse_weighted_prompt_tags(positive_prompt)
    negative_prompt_weight_tags = parse_weighted_prompt_tags(negative_prompt)

    # --------------------------------------- #
    # Separate Settings and CivitAI data
    # --------------------------------------- #
    match = re.search(r"(?P<settings>.*?)($|(?P<civitai>civitai resources:.*))", settings, re.DOTALL | re.IGNORECASE)
    settings = match.groupdict()["settings"]
    civitai_segment = match.groupdict()["civitai"]

    # --------------------------------------- #
    # Parse Settings into dictionary
    # --------------------------------------- #
    settings_dict: dict | None = None
    
    if settings:
        # Updated regex to properly capture JSON
        pattern = re.compile(
            r"(\w[\w\s]*?):\s*(\{.*?\}|\[[^\]]*\]|\"[^\"]*\"|[^,\n]+)",
            re.DOTALL | re.IGNORECASE
        )

        pairs = pattern.findall(settings)

        # Convert to dictionary
        settings_dict = {key.strip(): value.strip() for key, value in pairs}
    
    standard_keys = {}
    for setting_key in [_ for _ in settings_dict.keys()]:
        if "steps" in setting_key.lower():
            settings_dict["steps"] = settings_dict.pop(setting_key)
            standard_keys["steps"] = setting_key
        elif "cfg scale" == setting_key.lower():
            settings_dict["cfg_scale"] = settings_dict.pop(setting_key)
            standard_keys["cfg_scale"] = setting_key
        elif "seed" in setting_key.lower():
            settings_dict["seed"] = settings_dict.pop(setting_key)
            standard_keys["seed"] = setting_key
        elif "size" in setting_key.lower():
            settings_dict["size"] = settings_dict.pop(setting_key)
            standard_keys["size"] = setting_key
        elif "clip skip" == setting_key.lower():
            settings_dict["clip_skip"] = settings_dict.pop(setting_key)
            standard_keys["clip_skip"] = setting_key
        elif "denoising strength" == setting_key.lower():
            settings_dict["denoising_strength"] = settings_dict.pop(setting_key)
            standard_keys["denoising_strength"] = setting_key
        elif "model" == setting_key.lower():
            settings_dict["model"] = settings_dict.pop(setting_key)
            standard_keys["model"] = setting_key
        elif "model hash" in setting_key.lower():
            settings_dict["model_hash"] = settings_dict.pop(setting_key)
            standard_keys["model_hash"] = setting_key
        elif "lora hashes" == setting_key.lower():
            lora_hashes: str = settings_dict.pop(setting_key)
            lora_hashes = lora_hashes.strip().strip('\"').strip()
            lora_hash_data = {}
            for lh in lora_hashes.split(","):
                lora_name, lora_hash_id = lh.split(":")
                lora_hash_data[lora_name.strip()] = lora_hash_id.strip()
            settings_dict["lora_hashes"] = lora_hash_data
            standard_keys["lora_hashes"] = setting_key
        elif "version" == setting_key.lower():
            settings_dict["version"] = settings_dict.pop(setting_key)
            standard_keys["version"] = setting_key
        elif "sampler" == setting_key.lower():
            settings_dict["sampler"] = settings_dict.pop(setting_key)
            standard_keys["sampler"] = setting_key
        elif "schedule type" == setting_key.lower():
            settings_dict["schedule_type"] = settings_dict.pop(setting_key)
            standard_keys["schedule_type"] = setting_key
        elif "vae" == setting_key.lower():
            settings_dict["vae"] = settings_dict.pop(setting_key)
            standard_keys["vae"] = setting_key
        
    for setting_key in [_ for _ in settings_dict.keys()]:
        if setting_key not in standard_keys:
            settings_dict[f"_{setting_key}"] = settings_dict.pop(setting_key)


    # --------------------------------------- #
    # Read CivitAI JSON data to dictionary
    # --------------------------------------- #
    civitai_resources = None
    civitai_metadata = None
    
    if civitai_segment:
        match = re.search(r"((civitai resources:)(?P<rsrcs>.*?))($|civitai metadata:(?P<md>.*))", civitai_segment, re.DOTALL | re.IGNORECASE)
        civitai_resources = match.groupdict()["rsrcs"]
        civitai_metadata = match.groupdict()["md"]

        if isinstance(civitai_resources, str):
            civitai_resources = civitai_resources.strip().strip(",").strip()
        if isinstance(civitai_metadata, str):
            civitai_metadata = civitai_metadata.strip().strip(",").strip()

    if civitai_resources:
        civitai_resources = json.loads(civitai_resources)

        # --------------------------------------------- #
        # * Fill in Schedule type in 'settings_dict'
        # --------------------------------------------- #
        for setting_key, sampler_sched_tuple in CIVITAI_SAMPLER_DROPDOWN_MAP.items():
            if settings_dict["sampler"] == setting_key:
                settings_dict.pop("sampler") # Just doing this to keep 'sampler' and 'schedule type' keys together
                settings_dict["sampler"] = sampler_sched_tuple[0]
                settings_dict["schedule_type"] = sampler_sched_tuple[1]
                break
        
        # --------------------------------------------- #
        # * Lookup model data from API
        # --------------------------------------------- #
        model_version_ids = [str(x["modelVersionId"]).strip() for x in civitai_resources]
        if len(model_version_ids) > 0:
            # resources_data = bulk_resource_lookup(model_version_ids)
            resources_data = civitai.get_model_versions(version_ids=model_version_ids)

            for resource in civitai_resources:
                resource_data = [x for x in resources_data if x["id"] == resource["modelVersionId"]]
                if len(resource_data) > 0:
                    resource["base_model"] = resource_data[0]["baseModel"]
                    resource["model_id"] = resource_data[0]["modelId"]
                    resource["model_name"] = resource_data[0]["model"]["name"]
                    resource["model_version_id"] = resource_data[0]["id"]
                    resource["model_version_name"] = resource_data[0]["name"]
                    resource["sub_type"] = resource_data[0]["model"]["type"]
                    resource["trained_words"] = resource_data[0]["trainedWords"]
                    for f in resource_data[0]["files"]:
                        if f["primary"] == True:
                            resource["model_filename"] = f["name"]
                            resource["model_filetype"] = f["metadata"]["format"]
                            resource["model_fileext"] = "".join(Path(resource["model_filename"]).suffix)
                            resource["model_hashes"] = f["hashes"]
                
                # --------------------------------------------- #
                # * Get Model Name if not already populated
                # --------------------------------------------- #
                if "model" not in settings_dict:
                    if resource.get("type", "").lower() in ("checkpoint", "base model"):
                        settings_dict["model"] = resource["model_name"]
                        standard_keys["model"] = "Model"

                # --------------------------------------------- #
                # * Get VAE if not already populated
                # --------------------------------------------- #
                if "vae" not in settings_dict and (resource.get("type", "").lower() == "vae" or resource["sub_type"] == "vae"):
                    settings_dict["vae"] = resource["model_name"]
                    standard_keys["vae"] = "VAE"


    if "model" not in settings_dict:
        for rsrc in civitai_resources:
            if rsrc.get("sub_type", "").lower() in ("checkpoint", "base model"):
                settings_dict["model"] = rsrc.get("model_filename", "").replace(
                    rsrc.get("model_fileext", ""),
                    ""
                )
                break

    if civitai_metadata:
        civitai_metadata = json.loads(civitai_metadata)

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
        "civitai_resources": civitai_resources,
        "civitai_metadata": civitai_metadata,
    }
    
    return generation_data



def _parse_basic(raw_prompt_string):
    match = re.search(r"(?P<prompts>.*?)(?P<settings>steps:.*)", raw_prompt_string, re.DOTALL | re.IGNORECASE)
    prompts = match.groupdict()["prompts"]
    settings = match.groupdict()["settings"]

    # --------------------------------------- #
    # Prompt strings
    # --------------------------------------- #
    match = re.search(r"^(?P<pos>.*?)(?:\bnegative prompt:\s*(?P<neg>.*))?$", prompts, re.DOTALL | re.IGNORECASE)

    positive_prompt = match.groupdict()["pos"]
    negative_prompt = match.groupdict()["neg"]


    if isinstance(positive_prompt, str):
        positive_prompt = positive_prompt.strip().strip(",").strip()
    if isinstance(negative_prompt, str):
        negative_prompt = negative_prompt.strip().strip(",").strip()

    # --------------------------------------- #
    # Read LoRA and Embedding data
    # --------------------------------------- #
    lora_weights = re.findall(r"<lora:(?P<name>.*?):?(?P<weight>\d+|\d+\.\d+)?>", positive_prompt, re.DOTALL | re.IGNORECASE)
    embed_weights = re.findall(r"<embed:(?P<name>.*?):?(?P<weight>\d+|\d+\.\d+)?>", positive_prompt, re.DOTALL | re.IGNORECASE)
    lora_weights = [[x[0], float(x[1])] for x in lora_weights]
    embed_weights = [[x[0], float(x[1])] for x in embed_weights]

    # --------------------------------------- #
    # Get Weighted Prompt Tags
    # --------------------------------------- #
    positive_prompt_weight_tags = parse_weighted_prompt_tags(positive_prompt)
    negative_prompt_weight_tags = parse_weighted_prompt_tags(negative_prompt)

    # --------------------------------------- #
    # Separate Settings and CivitAI data
    # --------------------------------------- #
    match = re.search(r"(?P<settings>.*?)($|(?P<civitai>civitai resources:.*))", settings, re.DOTALL | re.IGNORECASE)
    settings = match.groupdict()["settings"]
    civitai = match.groupdict()["civitai"]

    # --------------------------------------- #
    # Parse Settings into dictionary
    # --------------------------------------- #
    settings_dict: dict | None = None
    
    if settings:
        # Updated regex to properly capture JSON
        pattern = re.compile(
            r"(\w[\w\s]*?):\s*(\{.*?\}|\[[^\]]*\]|\"[^\"]*\"|[^,\n]+)",
            re.DOTALL | re.IGNORECASE
        )

        pairs = pattern.findall(settings)

        # Convert to dictionary
        settings_dict = {key.strip(): value.strip() for key, value in pairs}
    
    standard_keys = {}
    for setting_key in [_ for _ in settings_dict.keys()]:
        if "steps" in setting_key.lower():
            settings_dict["steps"] = settings_dict.pop(setting_key)
            standard_keys["steps"] = setting_key
        elif "cfg scale" == setting_key.lower():
            settings_dict["cfg_scale"] = settings_dict.pop(setting_key)
            standard_keys["cfg_scale"] = setting_key
        elif "seed" in setting_key.lower():
            settings_dict["seed"] = settings_dict.pop(setting_key)
            standard_keys["seed"] = setting_key
        elif "size" in setting_key.lower():
            settings_dict["size"] = settings_dict.pop(setting_key)
            standard_keys["size"] = setting_key
        elif "clip skip" == setting_key.lower():
            settings_dict["clip_skip"] = settings_dict.pop(setting_key)
            standard_keys["clip_skip"] = setting_key
        elif "denoising strength" == setting_key.lower():
            settings_dict["denoising_strength"] = settings_dict.pop(setting_key)
            standard_keys["denoising_strength"] = setting_key
        elif "model" == setting_key.lower():
            settings_dict["model"] = settings_dict.pop(setting_key)
            standard_keys["model"] = setting_key
        elif "model hash" in setting_key.lower():
            settings_dict["model_hash"] = settings_dict.pop(setting_key)
            standard_keys["model_hash"] = setting_key
        elif "lora hashes" == setting_key.lower():
            lora_hashes: str = settings_dict.pop(setting_key)
            lora_hashes = lora_hashes.strip().strip('\"').strip()
            lora_hash_data = {}
            for lh in lora_hashes.split(","):
                lora_name, lora_hash_id = lh.split(":")
                lora_hash_data[lora_name.strip()] = lora_hash_id.strip()
            settings_dict["lora_hashes"] = lora_hash_data
            standard_keys["lora_hashes"] = setting_key
        elif "version" == setting_key.lower():
            settings_dict["version"] = settings_dict.pop(setting_key)
            standard_keys["version"] = setting_key
        elif "sampler" == setting_key.lower():
            settings_dict["sampler"] = settings_dict.pop(setting_key)
            standard_keys["sampler"] = setting_key
        elif "schedule type" == setting_key.lower():
            settings_dict["schedule_type"] = settings_dict.pop(setting_key)
            standard_keys["schedule_type"] = setting_key
        elif "vae" == setting_key.lower():
            settings_dict["vae"] = settings_dict.pop(setting_key)
            standard_keys["vae"] = setting_key
        
    for setting_key in [_ for _ in settings_dict.keys()]:
        if setting_key not in standard_keys:
            settings_dict[f"_{setting_key}"] = settings_dict.pop(setting_key)


    # --------------------------------------- #
    # Read CivitAI JSON data to dictionary
    # --------------------------------------- #
    resources = []
    metadata = {}
    
    if civitai:
        match = re.search(r"((civitai resources:)(?P<rsrcs>.*?))($|civitai metadata:(?P<md>.*))", civitai, re.DOTALL | re.IGNORECASE)
        resources = match.groupdict()["rsrcs"]
        metadata = match.groupdict()["md"]

        if isinstance(resources, str):
            resources = resources.strip().strip(",").strip()
        if isinstance(metadata, str):
            metadata = metadata.strip().strip(",").strip()

    if resources:
        resources = json.loads(resources)

        # --------------------------------------------- #
        # * Fill in Schedule type in 'settings_dict'
        # --------------------------------------------- #
        for setting_key, sampler_sched_tuple in CIVITAI_SAMPLERS.items():
            if settings_dict["sampler"] == setting_key:
                settings_dict.pop("sampler") # Just doing this to keep 'sampler' and 'schedule_type' keys together
                settings_dict["sampler"] = sampler_sched_tuple[0]
                settings_dict["schedule_type"] = sampler_sched_tuple[1]
                break
        
        # --------------------------------------------- #
        # * Lookup model data from API
        # --------------------------------------------- #
        model_version_ids = [str(x["modelVersionId"]).strip() for x in resources]
        if len(model_version_ids) > 0:
            resources_data = bulk_resource_lookup(model_version_ids)

            for resource in resources:
                resource_data = [x for x in resources_data if x["id"] == resource["modelVersionId"]]
                if len(resource_data) > 0:
                    resource["base_model"] = resource_data[0]["baseModel"]
                    resource["model_id"] = resource_data[0]["modelId"]
                    resource["model_name"] = resource_data[0]["model"]["name"]
                    resource["model_version_name"] = resource_data[0]["name"]
                    resource["sub_type"] = resource_data[0]["model"]["type"]
                    resource["trained_words"] = resource_data[0]["trainedWords"]
                    for f in resource_data[0]["files"]:
                        if f["primary"] == True:
                            resource["model_filename"] = f["name"]
                            resource["model_filetype"] = f["metadata"]["format"]
                            resource["model_fileext"] = "".join(Path(resource["model_filename"]).suffix)
                
                # --------------------------------------------- #
                # * Get Model Name if not already populated
                # --------------------------------------------- #
                if "model" not in settings_dict:
                    if resource.get("type", "").lower() in ("checkpoint", "base model"):
                        settings_dict["model"] = resource["model_name"]
                        standard_keys["model"] = "Model"

                # --------------------------------------------- #
                # * Get VAE if not already populated
                # --------------------------------------------- #
                if "vae" not in settings_dict and (resource.get("type", "").lower() == "vae" or resource["sub_type"] == "vae"):
                    settings_dict["vae"] = resource["model_name"]
                    standard_keys["vae"] = "VAE"


    if "model" not in settings_dict:
        for rsrc in resources:
            if rsrc.get("sub_type", "").lower() in ("checkpoint", "base model"):
                settings_dict["model"] = rsrc.get("model_filename", "").replace(
                    rsrc.get("model_fileext", ""),
                    ""
                )
                break


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
        "resources": resource,
        "metadata": {}
    }
    
    return generation_data



