from src.api import get_pillow_image_object
from src.api import extract_prompt_from_image
from src.api import parse_prompt_string
from src.color import console, cprint


# A1111 (txt2img)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/txt2img-images/2025-10-29/00090-2954401898.png')

# A1111 (img2img)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/Millie/00191-177736047 (1).png')

# CivitAI (txt2img)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/Millie/2025-10-29T05.54.12_1.jpg')
image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/civitai downloads/CivitAI Backup (2025-04-03)/MB53J3KT3A8173Z9EDAVM1GF50.jpeg')

# Tensor.art () (euler_a)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/tensorart downloads/839995560707668303.png')

# Tensor.art (txt2img) (dpm2pp karras)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/tensorart downloads/masterpiec-1847869443-17_33_59-1.png')

# Tensor.art (img2img)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/tensorart downloads/masterpiec-1847869445-22_21_06.png')

# Tensor.art (img2img) (lora and embedding)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/tensorart downloads/masterpiec-1847869446-22_30_15-1.png')

# Tensor.art (inpaint) (lora and embedding)
# image = get_pillow_image_object('/Users/joseph/Library/CloudStorage/GoogleDrive-mangabox76@gmail.com/My Drive/a1111/outputs/tensorart downloads/masterpiec-1847869445-22_39_07.png')

# ComfyUI (txt2img) (checkpoint only)
# image = get_pillow_image_object('/Users/joseph/Documents/ComfyUI/output/myla_00002_.png')

prompt = extract_prompt_from_image(image)
print("FULL PROMPT STRING:\n------------------------")
console.print(prompt)
print()

gendata = parse_prompt_string(prompt)
print("GEN DATA:\n---------------")
console.print_json(data=gendata)
print()