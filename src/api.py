import io
import re
import json
from pathlib import Path
from collections import OrderedDict

from PIL import Image
from PIL.ExifTags import TAGS

from .color import cprint, console

SAMPLERS = {
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

class SettingsDict(OrderedDict):
    def __init__(self, _dict:dict):
        # Initialize the base OrderedDict with any provided args/kwargs
        super().__init__()
        
        # Define default keys and values
        default_keys = [
            "steps",
            "cfg_scale",
            "seed",
            "sampler",
            "schedule_type",
            "model",
            "width",
            "height",
            "size",
        ]
        
        for key in default_keys:
            self.setdefault(key, _dict.get(key, None))
        
        for k, v in _dict.items():
            if k not in default_keys:
                self.setdefault(k, v)


def get_pillow_image_object(obj: str | Path | io.BytesIO | Image.Image) -> Image.Image | None:
    if isinstance(obj, Image.Image):
        return obj

    elif isinstance(obj, (str, Path)):
        if isinstance(obj, str):
            obj = obj.strip()
        with Image.open(Path(obj).resolve()) as image:
            return image
    
    elif isinstance(obj, io.BytesIO):
        with Image.open(obj) as image:
            return image
    
    return None


def extract_prompt_from_image(image_or_path: str | Path | io.BytesIO | Image.Image):
    image = get_pillow_image_object(image_or_path)
    assert(image != None)
    prompt_str = ""

    if "parameters" in image.info.keys():
        prompt_str = image.info["parameters"]

    elif "prompt" in image.info.keys() and "generation_data" in image.info.keys():
        # Tensor Art
        prompt = json.loads(image.info["prompt"])
        gen_data = json.loads(image.info["generation_data"].replace("\x00", ""))

        prompt_str = "TENSOR-ART__" + json.dumps({"prompt": prompt, "generation_data": gen_data})
    
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
            try:
                # Might be COMFYUI
                comfy_prompt = json.loads(image.info["prompt"])
                comfy_workflow = json.loads(image.info["workflow"])
                prompt_str = "COMFYUI__" + json.dumps({"prompt": comfy_prompt, "workflow": comfy_workflow})
            except:
                exif_bytes: bytes = image.info["exif"]

                if b"UNICODE" in exif_bytes:
                    prompt_str = exif_bytes[exif_bytes.find(b"UNICODE") + 7:].decode("utf-8")
                else:
                    cprint.bright_red("Couldn't find data in exif byte string")

    prompt_str = prompt_str.replace("\x00", "")

    return prompt_str


def parse_prompt_string(raw_prompt_string, **kwargs):
    json_data = None
    extra_metadata = None

    # Tensor.Art gen data
    if "TENSOR-ART__" in raw_prompt_string:
        raw_prompt_string = raw_prompt_string.replace("TENSOR-ART__", "")
        json_data = json.loads(raw_prompt_string)
        gen_data = json_data["generation_data"]
        # console.print(json_data)
        # console.print(gen_data)

        lora_models = []
        embed_models = []
        
        # Loras
        for model in gen_data.get("models", []):
            if model.get("type", "").lower() == "lora":
                # lora_models.append([model.get("modelFileName"), model.get("weight")])
                lora_models.append(model)
        
        # Embeddings
        for model in gen_data.get("embeddingModels", []):
            # embed_models.append([model.get("modelFileName"), model.get("weight")])
            embed_models.append(model)

        generation_data = {
            "positive": gen_data["prompt"],
            "negative": gen_data["negativePrompt"],
            "settings": {
                "steps": gen_data["steps"],
                "cfg_scale": gen_data["cfgScale"],
                "seed": gen_data["seed"],
                "sampler": gen_data["ksamplerName"],
                "schedule_type": gen_data["schedule"],
                "model": gen_data.get("baseModel", {}).get("modelFileName"),
                "width": gen_data["width"],
                "height": gen_data["height"],
                "size": f"{gen_data['width']}x{gen_data['height']}",
            },
            "loras": lora_models,
            "embeds": embed_models,
        }
        return generation_data
    
    if "COMFYUI__" in raw_prompt_string:
        raw_prompt_string = raw_prompt_string.replace("COMFYUI__", "")
        json_data = json.loads(raw_prompt_string)
        node_data = json_data["prompt"]
        for node_key, node in node_data.items():
            if node["class_type"] == "KSampler":
                inputs = node.get("inputs", {})
                sampler_name = inputs.get("sampler_name")
                scheduler = inputs.get("scheduler")
                cfg = inputs.get("cfg")
                steps = inputs.get("steps")
                seed = inputs.get("seed")
                
                checkpoint_key, checkpoint_clip = inputs.get("model", [None, None])
                pos_prompt_key, pos_prompt_clip = inputs.get("positive", [None, None])
                neg_prompt_key, neg_prompt_clip = inputs.get("negative", [None, None])
                latent_img_key, latent_img_clip = inputs.get("latent_image", [None, None])

                lora_models = []
                embed_models = []
                
                width = node_data[latent_img_key].get("inputs", {}).get("width")
                height = node_data[latent_img_key].get("inputs", {}).get("height")
                size = f"{width}x{height}" if (width, height) != (None, None) else None

                generation_data = {
                    "positive": node_data[pos_prompt_key].get("inputs", {}).get("text"),
                    "negative": node_data[neg_prompt_key].get("inputs", {}).get("text"),
                    "settings": {
                        "steps": steps,
                        "cfg_scale": cfg,
                        "seed": seed,
                        "sampler": sampler_name,
                        "schedule_type": scheduler,
                        "model": node_data[checkpoint_key].get("inputs", {}).get("ckpt_name"),
                        "width": width,
                        "height": height,
                        "size": size,
                    },
                    "loras": lora_models,
                    "embeds": embed_models,
                }
                return generation_data

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
            sampler = SAMPLERS.get(extra_metadata["sampler"], ['', ''])[0],
            scheduler = SAMPLERS.get(extra_metadata["sampler"], ['', ''])[1],
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
    
    if kwargs.get("prompts_only") == True:
        return {"positive": positive_prompt, "negative": negative_prompt}

    # --------------------------------------- #
    # Read LoRA and Embedding data
    # --------------------------------------- #
    lora_weights = re.findall(r"<lora:(?P<name>.*?):?(?P<weight>\d+|\d+\.\d+)?>", positive_prompt, re.DOTALL | re.IGNORECASE)
    embed_weights = re.findall(r"<embed:(?P<name>.*?):?(?P<weight>\d+|\d+\.\d+)?>", positive_prompt, re.DOTALL | re.IGNORECASE)
    lora_weights = [[x[0], float(x[1])] for x in lora_weights]
    embed_weights = [[x[0], float(x[1])] for x in embed_weights]

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
        for setting_key, sampler_sched_tuple in SAMPLERS.items():
            if settings_dict["sampler"] == setting_key:
                settings_dict.pop("sampler") # Just doing this to keep 'sampler' and 'schedule type' keys together
                settings_dict["sampler"] = sampler_sched_tuple[0]
                settings_dict["schedule_type"] = sampler_sched_tuple[1]
                break

    if "model" not in settings_dict:
        for rsrc in civitai_resources:
            if rsrc.get("type", "").lower() in ("checkpoint", "base model"):
            # if rsrc.get("sub_type", "").lower() in ("checkpoint", "base model"):
                default_model_name = rsrc.get("modelName")
                default_model_version_name = rsrc.get("modelVersionName")
                default_name = default_model_name
                if default_model_version_name != None:
                    default_name = f"{default_model_name} [{default_model_version_name}]"
                settings_dict["model"] = rsrc.get("model_filename", default_name)
                # settings_dict["model"] = rsrc.get("model_filename", "").replace(
                #     rsrc.get("model_fileext", ""),
                #     ""
                # )
                break

    if civitai_metadata:
        civitai_metadata = json.loads(civitai_metadata)
    
    # console.print_json(data=civitai_resources)

    width, height = settings_dict.get("size", "-x-").split("x")
    width = width if width != "-" else None
    height = height if height != "-" else None
    settings_dict["width"] = width
    settings_dict["height"] = height
    
    settings_dict = dict(SettingsDict(settings_dict))
    generation_data = {
        "positive": positive_prompt,
        "negative": negative_prompt,
        "settings": settings_dict,
        "loras": [],
        "embeds": [],
    }
    
    return generation_data

