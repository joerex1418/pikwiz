import sys
import pathlib

from src.parse import ImageData
from src.util import resize_image
from src.util import resize_bulk_from_web
from src.parse import extract_prompt_from_image
from src.parse import parse_prompt_string
from src.color import cprint, color
from PIL.ExifTags import TAGS


urllist = [
    "https://orchestration.civitai.com/v2/consumer/blobs/45SDJNQW7WBK54VRABVSYAHST0.jpeg",
    "https://orchestration.civitai.com/v2/consumer/blobs/NZWNS3V3W20G7EMDVKQBZJMYQ0.jpeg",
    "https://orchestration.civitai.com/v2/consumer/blobs/0AV0FJ2W3R8927KCTX9KXMPD10.jpeg",
    "https://orchestration.civitai.com/v2/consumer/blobs/R8BWCFWB7FNG96AQXZKCTV1E00.jpeg",
    "https://orchestration.civitai.com/v2/consumer/blobs/QRDQX00P0B672A7QRJCVQEK880.jpeg",
    ]

new_images, og_images = resize_bulk_from_web(urllist, factor=0.5, return_originals=True)


img = og_images[0]

new = ImageData(new_images[0])
og = ImageData(og_images[0])

# print(new.raw_prompt)
print(new_images[0].info["url"])



