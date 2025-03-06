from enum import Enum


ASPECT_RATIOS = {
    "SD1": {
        "square": "512x512",
        "landscape": "768x512",
        "portrait": "512x768"
    },
    "SDXL": {
        "square": "1024x1024",
        "landscape": "1216x832",
        "portrait": "832x1216"
    },
    "Pony": {
        "square": "1024x1024",
        "landscape": "1216x832",
        "portrait": "832x1216"
    },
    "Illustrious": {
        "square": "1024x1024",
        "landscape": "1216x832",
        "portrait": "832x1216"
    },
    "NoobAI": {
        "square": "1024x1024",
        "landscape": "1216x832",
        "portrait": "832x1216"
    },
    "Flux1": {
        "square": "1024x1024",
        "landscape": "1216x832",
        "portrait": "832x1216"
    },
    "SD3": {
        "square": "1024x1024",
        "landscape": "1216x832",
        "portrait": "832x1216"
    },
    "SD3_5M": {
        "square": "1024x1024",
        "landscape": "1216x832",
        "portrait": "832x1216"
    },
    "Other": {}
}


SAMPLER_MAP = {
    "Euler a": {"sampler_civitai": "EulerA", "sampler_comfy": "euler_ancestral", "scheduler": "normal"},
    "Euler": {"sampler_civitai": "Euler", "sampler_comfy": "euler", "scheduler": "normal"},
    "LMS": {"sampler_civitai": "LMS", "sampler_comfy": "lms", "scheduler": "normal"},
    "Heun": {"sampler_civitai": "Heun", "sampler_comfy": "heun", "scheduler": "normal"},
    "DPM2": {"sampler_civitai": "DPM2", "sampler_comfy": "dpmpp_2", "scheduler": "normal"},
    "DPM2 a": {"sampler_civitai": "DPM2A", "sampler_comfy": "dpmpp_2_ancestral", "scheduler": "normal"},
    "DPM++ 2S a": {"sampler_civitai": "DPM2SA", "sampler_comfy": "dpmpp_2s_ancestral", "scheduler": "normal"},
    "DPM++ 2M": {"sampler_civitai": "DPM2M", "sampler_comfy": "dpmpp_2m", "scheduler": "normal"},
    "DPM++ 2M SDE": {"sampler_civitai": "DPM2MSDE", "sampler_comfy": "dpmpp_2m_sde", "scheduler": "normal"},
    "DPM++ SDE": {"sampler_civitai": "DPMSDE", "sampler_comfy": "dpmpp_sde", "scheduler": "normal"},
    "DPM fast": {"sampler_civitai": "DPMFast", "sampler_comfy": "dpm_fast", "scheduler": "normal"},
    "DPM adaptive": {"sampler_civitai": "DPMAdaptive", "sampler_comfy": "dpm_adaptive", "scheduler": "normal"},
    "LMS Karras": {"sampler_civitai": "LMSKarras", "sampler_comfy": "lms", "scheduler": "karras"},
    "DPM2 Karras": {"sampler_civitai": "DPM2Karras", "sampler_comfy": "dpm_2", "scheduler": "karras"},
    "DPM2 a Karras": {"sampler_civitai": "DPM2AKarras", "sampler_comfy": "dpm_2_ancestral", "scheduler": "karras"},
    "DPM++ 2S a Karras": {"sampler_civitai": "DPM2SAKarras", "sampler_comfy": "dpmpp_2s_ancestral", "scheduler": "karras"},
    "DPM++ 2M Karras": {"sampler_civitai": "DPM2MKarras", "sampler_comfy": "dpmpp_2m", "scheduler": "karras"},
    "DPM++ 2M SDE Karras": {"sampler_civitai": "DPM2MSDEKarras", "sampler_comfy": "dpmpp_2m_sde", "scheduler": "karras"},
    "DPM++ SDE Karras": {"sampler_civitai": "DPMSDEKarras", "sampler_comfy": "dpmpp_sde", "scheduler": "karras"},
    "DPM++ 3M SDE": {"sampler_civitai": "DPM3MSDE", "sampler_comfy": "dpmpp_3m_sde", "scheduler": "normal"},
    "DPM++ 3M SDE Karras": {"sampler_civitai": "DPM3MSDEKarras", "sampler_comfy": "dpmpp_3m_sde", "scheduler": "karras"},
    "DPM++ 3M SDE Exponential": {"sampler_civitai": "DPM3MSDEExponential", "sampler_comfy": "dpmpp_3m_sde", "scheduler": "exponential"},
    "DDIM": {"sampler_civitai": "DDIM", "sampler_comfy": "ddim", "scheduler": "normal"},
    "PLMS": {"sampler_civitai": "PLMS", "sampler_comfy": "plms", "scheduler": "normal"},
    "UniPC": {"sampler_civitai": "UniPC", "sampler_comfy": "uni_pc", "scheduler": "normal"},
    "LCM": {"sampler_civitai": "LCM", "sampler_comfy": "lcm", "scheduler": "normal"},
    "undefined": {"sampler_civitai": "undefined", "sampler_comfy": "dpmpp_2m", "scheduler": "karras"},
}


CIVITAI_SAMPLER_DROPDOWN_MAP = {
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


class Sampler(Enum):
    EULERA = "EulerA"
    EULER = "Euler"
    LMS = "LMS"
    HEUN = "Heun"
    DPM2 = "DPM2"
    DPM2A = "DPM2A"
    DPM2SA = "DPM2SA"
    DPM2M = "DPM2M"
    DPMSDE = "DPMSDE"
    DPMFAST = "DPMFast"
    DPMADAPTIVE = "DPMAdaptive"
    LMSKARRAS = "LMSKarras"
    DPM2KARRAS = "DPM2Karras"
    DPM2AKARRAS = "DPM2AKarras"
    DPM2MKARRAS = "DPM2MKarras"
    DPMSDEKARRAS = "DPMSDEKarras"
    DDIM = "DDIM"
    PLMS = "PLMS"
    UNIPC = "UniPC"
    UNDEFINED = "undefined"
    LCM = "LCM"

    @property
    def civitai(self) -> str:
        """Returns the civitai code for the sampler."""
        return self.value

    @property
    def comfy(self) -> str:
        """Returns the comfy code for the sampler."""
        for key, value in SAMPLER_MAP.items():
            if self.value == value["sampler_civitai"]:
                return value["sampler_comfy"]
        return "undefined"

    @property
    def scheduler(self) -> str:
        """Returns the scheduler type for the sampler."""
        for key, value in SAMPLER_MAP.items():
            if self.value == value["sampler_civitai"]:
                return value["scheduler"]
        return "normal"
    

class ModelSort(Enum):
    NEWEST = "Newest"
    OLDEST = "Oldest"
    HIGHEST_RATED = "Highest Rated"
    MOST_LIKED = "Most Liked"
    MOST_COLLECTED = "Most Collected"
    MOST_DOWNLOADED = "Most Downloaded"
    MOST_DISCUSSED = "Most Discussed"
    MOST_IMAGES = "Most Images"

    def __init__(self, _name):
        self._name = _name
    
    @property
    def name(self) -> str:
        return self._name
    

class Sort(Enum):
    NEWEST = "Newest"
    OLDEST = "Oldest"
    MOST_REACTIONS = "Most Reactions"
    MOST_COMMENTS = "Most Comments"
    MOST_COLLECTED = "Most Collected"

    def __init__(self, _name):
        self._name = _name
    
    @property
    def name(self) -> str:
        return self._name
    

class Tool(Enum):
    ZEBRA10 = ("10zebra", 164)
    A1111 = ("A1111", 84)
    ABLETON = ("Ableton", 301)
    ADOBE_AFTEREFFECTS = ("Adobe AfterEffects", 63)
    ADOBE_FIREFLY = ("Adobe Firefly", 4)
    ADOBE_PHOTOSHOP = ("Adobe Photoshop", 62)
    ADOBE_PODCAST = ("Adobe Podcast", 50)
    ADOBE_PREMIERE = ("Adobe Premiere", 127)
    AICU = ("AICU", 269)
    AIHUB = ("AIHUB", 275)
    AI_KOREA_COMMUNITY = ("AI Korea Community", 270)
    AI_MUSIC = ("AI Music", 292)
    ANIFUSION = ("AniFusion", 129)
    ANIMATEDIFF = ("AnimateDiff", 171)
    ARTFLOW = ("Artflow", 252)
    ARTLIST = ("Artlist", 277)
    AUDACITY = ("Audacity", 136)
    AUDIMEE = ("Audimee", 299)
    BANDLAB_SPLITTER = ("BandLab Splitter", 161)
    BANODOCO = ("Banodoco", 70)
    BASEDLABSAI = ("BasedLabsAI", 200)
    BITWIG = ("Bitwig", 244)
    BLENDER = ("Blender", 263)
    BOOM_BOX_STUDIO = ("Boom Box Studio", 297)
    BOXIMATOR = ("Boximator", 102)
    BREV = ("Brev", 26)
    CANVA = ("Canva", 152)
    CAPCUT = ("CapCut", 81)
    CARTESIA = ("Cartesia", 178)
    CC4 = ("CC4", 264)
    CHATGPT = ("ChatGPT", 150)
    CIVITAI = ("Civitai", 78)
    CLIP_CHAMP = ("Clip Champ", 246)
    COGVIDEOX = ("CogVideoX", 184)
    COMFY_COMMUNITY_SUMMIT_WAY_TO_AGI = ("Comfy Community Summit / Way To AGI", 267)
    COMFYUI = ("ComfyUI", 86)
    CRAIYON = ("Craiyon", 93)
    CUBASE_ = ("Cubase ", 298)
    CUEBRIC = ("Cuebric", 111)
    DALL_E_3 = ("DALL-E 3", 73)
    DAVANT = ("Davant", 165)
    DAVINCI = ("DaVinci", 109)
    DAVINCI_RESOLVE = ("DaVinci Resolve", 80)
    DEEP_DREAM_GENERATOR = ("Deep Dream Generator", 130)
    DEEPMAKE = ("DeepMake", 120)
    DEEPMOTION = ("DeepMotion", 43)
    DEFORUM_STUDIO = ("Deforum Studio", 7)
    DIFFUS = ("Diffus", 108)
    DOMO_AI = ("Domo AI", 10)
    DRAW_THINGS = ("Draw Things", 139)
    DREAM = ("Dream", 89)
    DREAMINA_ = ("Dreamina ", 259)
    DREAMSTUDIO = ("DreamStudio", 72)
    DZINE = ("Dzine", 257)
    EBSYNTH = ("EBSynth", 9)
    EDENART = ("Eden.art", 300)
    ELEVENLABS = ("ElevenLabs", 21)
    ENVATO = ("Envato", 203)
    EPIDEMIC_SOUND = ("Epidemic Sound", 156)
    ESCAPEAI = ("Escape.ai", 280)
    FABLE = ("Fable", 5)
    FACEFUSION = ("FaceFusion", 287)
    FAL = ("fal", 190)
    FILAMEN_ZHONK_VISION = ("Filamen & Zhonk Vision", 271)
    FINAL_CUT_PRO = ("Final Cut Pro", 241)
    FLIMORA_ = ("Flimora ", 202)
    FL_STUDIO = ("FL Studio", 237)
    FLUSH = ("Flush", 97)
    FLUX = ("Flux", 199)
    FOOOCUS = ("Fooocus", 83)
    FORGE = ("Forge", 88)
    FREEPIK = ("Freepik", 189)
    FREESOUND = ("Freesound", 296)
    GEMINI = ("Gemini", 1)
    GENMO = ("Genmo", 128)
    GETTY_IMAGES_GENERATIVE_AI = ("Getty Images Generative AI", 94)
    GIMP = ("GIMP", 76)
    GLIF = ("glif", 250)
    GODOT = ("Godot", 29)
    GOENHANCE = ("GoEnhance", 293)
    GOOEY_AI = ("Gooey AI", 154)
    GOOGLE_IMAGEFX = ("Google ImageFX", 90)
    GROK = ("Grok", 284)
    HAILUO_AUDIO = ("Hailuo Audio", 260)
    HAIPER = ("Haiper", 65)
    HEDRA = ("Hedra", 140)
    HIGGSFIELD = ("Higgsfield", 177)
    HITFILM = ("Hitfilm", 148)
    HUGGING_FACE = ("Hugging Face", 302)
    HUNYUAN = ("HunYuan", 274)
    IDEOGRAM = ("Ideogram", 113)
    IKHOR_LABS = ("iKHOR Labs", 69)
    IMAGINEART = ("Imagine.art", 258)
    INVIDEO = ("Invideo", 236)
    INVOKE = ("Invoke", 87)
    JIMENG = ("Jimeng", 288)
    JOYCLIP = ("Joyclip", 283)
    KAIBER = ("Kaiber", 8)
    KITTL_AI = ("Kittl AI", 153)
    KLING = ("Kling", 166)
    KOLORS = ("Kolors", 167)
    KREA = ("KREA", 2)
    KRITA = ("Krita", 77)
    LAMBDA_LABS = ("Lambda Labs", 255)
    LASCOAI_ = ("Lasco.ai ", 151)
    LENSGO = ("LensGo", 41)
    LEONARDOAI = ("Leonardo.ai", 3)
    LIGHTRICKS_LTXV = ("Lightricks LTXV", 170)
    LIPDUB = ("LipDub", 290)
    LIVE_PORTRAIT = ("Live Portrait", 143)
    LOOPCLOUD = ("Loopcloud", 243)
    LOUDME_AI = ("LoudMe AI", 245)
    LTX_STUDIO = ("LTX Studio", 141)
    LUMA_DREAM_MACHINE = ("Luma Dream Machine", 124)
    LUMA_GENIE = ("Luma Genie", 125)
    MACHINE_CINEMA = ("Machine Cinema", 266)
    MAGE = ("Mage", 157)
    MAGIC_ANIMATE = ("Magic Animate", 135)
    MAGIX_VIDEO = ("Magix Video", 242)
    MAGNIFIC = ("MAGNIFIC", 47)
    MAGO = ("Mago", 276)
    MAZE = ("Maze", 131)
    META_AI = ("Meta AI", 96)
    MIAOHUA = ("Miaohua", 289)
    MICROSOFT_DESIGNER = ("Microsoft Designer", 91)
    MIDJOURNEY = ("Midjourney", 30)
    MIMICMOTION = ("MimicMotion", 142)
    MINIMAX_HAILUO = ("MiniMax / Hailuo", 172)
    MIXCRAFT = ("Mixcraft", 162)
    MMAUDIO = (" MMAudio", 248)
    MOCHI = ("Mochi", 169)
    MODELSLAB = ("ModelsLab", 106)
    MORPH_STUDIO = ("Morph Studio", 66)
    MOVE_AI = ("Move AI", 44)
    NEBIUS = ("Nebius", 174)
    NEURAL_FRAMES = ("neural frames", 121)
    NIJIJOURNEY = ("Nijijourney", 82)
    NIJIVOICE = ("Nijivoice", 281)
    NIM = ("Nim", 201)
    OLIVIO_SARIKAS = ("Olivio Sarikas", 273)
    OPENART = ("OpenArt", 107)
    PARSEQ = ("Parseq", 85)
    PHOTOPEA = ("Photopea", 64)
    PICLUMEN = ("Piclumen", 278)
    PICSART = ("Picsart", 196)
    PICSO = ("PicSo", 138)
    PIKA = ("Pika", 67)
    PINOKIO = ("Pinokio", 279)
    PIRATEDIFFUSION = ("PirateDiffusion", 103)
    PIXABAY = ("PixaBay", 253)
    PIXVERSE = ("Pixverse", 155)
    PLAIDAY = ("PlaiDay", 100)
    PLAYBOOK_3D = ("Playbook 3D", 188)
    PLAYGROUND = ("Playground", 101)
    PLAYHOUSE = ("Playhouse", 187)
    PLAY_HT = ("Play.ht", 291)
    PRISM = ("Prism", 39)
    PURPLESMART = ("Purplesmart", 185)
    RAY2 = ("Ray 2", 294)
    REALDREAMS = ("Realdreams", 272)
    RECRAFT = ("Recraft", 249)
    RENDERMIND = ("Rendermind", 286)
    ROKOKO = ("Rokoko", 15)
    RUBBRBAND = ("Rubbrband", 126)
    RUNDIFFUSION = ("RunDiffusion", 25)
    RUNPOD = ("RunPod", 24)
    RUNWAY = ("Runway", 68)
    SADTALKER = ("SadTalker", 137)
    SAGA = ("SAGA", 192)
    SALAD = ("Salad", 180)
    SALT = ("Salt", 75)
    SCENARIO = ("Scenario", 195)
    SDNEXT = ("SD.Next", 285)
    SEAART = ("SeaArt", 132)
    SHAKKER = ("Shakker", 262)
    SHOWRUNNER_AI = ("Showrunner AI", 99)
    SHUTTERSTOCK_AI_IMAGE_GENERATION = ("Shutterstock AI Image Generation", 95)
    SILMU = ("Silmu", 194)
    SORA = ("Sora", 240)
    SPLICE = ("Splice", 254)
    STABLE2GO = ("Stable2go", 104)
    STABLE_ARTISAN = ("Stable Artisan", 71)
    STABLE_AUDIO = ("Stable Audio", 19)
    STORY_DIFFUSION = ("Story Diffusion", 110)
    STORYTELLERAI = ("Storyteller.ai", 158)
    SUNO = ("Suno", 20)
    SWARMUI = ("SwarmUI", 168)
    SYNC = ("Sync", 179)
    TENSORART = ("Tensor.art", 238)
    TENSORPICS = ("TensorPics", 160)
    THINKDIFFUSION = ("ThinkDiffusion", 23)
    TOON_CRAFTER = ("Toon Crafter", 159)
    TOPAZ_PHOTO_AI = ("Topaz Photo AI", 48)
    TOPAZ_VIDEO_AI = ("Topaz Video AI", 49)
    TOUCH_DESIGNER = ("Touch Designer", 74)
    TRIPO_3D = ("Tripo 3D", 119)
    UDIO = ("Udio", 18)
    UNITY = ("Unity", 27)
    UNREAL_ENGINE = ("Unreal Engine", 61)
    UPPBEAT = ("Uppbeat", 261)
    VEEDIO = ("Veed.io", 204)
    VEO = ("Veo", 205)
    VIDPROC = ("VidProc", 133)
    VIDU = ("Vidu", 193)
    VIGGLE = ("Viggle", 11)
    VIMEO = ("Vimeo", 79)
    VOIA = ("Voia", 295)
    VSDC = ("VSDC", 134)
    WARP_VIDEO = ("Warp Video", 98)
    WONDER_DYNAMICS = ("Wonder Dynamics", 14)
    WONDERSHARE_ = ("Wondershare ", 251)
    WONDER_STUDIO = ("Wonder Studio", 46)
    WOWZER = ("Wowzer", 92)
    YODAYO = ("Yodayo", 105)
    ZEBRACAT = ("Zebracat", 256)
    ZERO1CINE = ("zero1cine", 268)

    def __init__(self, _name, _id):
        self._name = _name
        self._id = _id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def id(self) -> int:
        return self._id



class GenTag(Enum):
    GEN = "gen"
    IMG = "img"
    TXT2IMG = "txt2img"
    LIKED = "feedback:liked"
    DISLIKED = "feedback:disliked"
    FAVORITED = "favorite"
    
    def __init__(self, _name):
        self._name = _name
    
    @property
    def name(self) -> str:
        return self._name
    


class Technique(Enum):
    def __init__(self, _name, _id):
        self._name = _name
        self._id = _id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def id(self) -> int:
        return self._id
    
    TXT2IMG = ("txt2img", 1)
    IMG2IMG = ("img2img", 2)
    INPAINTING = ("inpainting", 3)
    WORKFLOW = ("workflow", 4)
    VID2VID = ("vid2vid", 5)
    TXT2VID = ("txt2vid", 6)
    IMG2VID = ("img2vid", 7)
    CONTROLNET = ("controlnet", 8)


class Period(Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"
    YEAR = "Year"
    ALLTIME = "AllTime"


class ModelType(Enum):
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


class CheckpointType(Enum):
    ALL = "all"
    TRAINED = "Trained"
    MERGE = "Merge"


class FileFormat(Enum):
    SAFETENSOR = "SafeTensor"
    PICKLETENSOR = "PickleTensor"
    GGUF = "GGUF"
    DIFFUSERS = "Diffusers"
    CORE_ML = "Core ML"
    ONNX = "ONNX"


class BaseModel(Enum):
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


