import io
import pathlib

import rich
import httpx
from PIL import Image
from PIL.ExifTags import TAGS



class ImageData:
    def __init__(self, data: str | io.BytesIO):
        if not isinstance(data, io.BytesIO):
            data = pathlib.Path(data).resolve()
        
        assert(data)

        with Image.open(data) as image:
            self.image = image

        # self.image = self._read_image()
        self.raw_prompt = self._get_raw_prompt()

    def _read_image(self) -> Image.Image:
        with Image.open(self.path) as image:
            return image


    def _get_raw_prompt(self) -> str | None:
        if self.image.format in ("PNG", "WEBP"):
            prompt_data = self.image.info["parameters"]
        
        elif self.image.format in ("JPEG", "JPG", "TIFF", "JFIF"):
            exif_data = self.image._getexif()
            if exif_data:
                exif_dict = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
                if "UserComment" in exif_dict:
                    raw_comment: bytes = exif_dict["UserComment"]
                    if raw_comment.startswith(b"UNICODE"):
                        prompt_data = raw_comment[7:].decode("utf-8")
        else:
            prompt_data = ""
        
        return prompt_data.replace("\x00", "")


