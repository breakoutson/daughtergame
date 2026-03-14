import urllib.request
import io
import os
from PIL import Image

BRAIN_DIR = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"
CLOTHES_GRID = os.path.join(BRAIN_DIR, "v10_clothes_grid_1773460054645.png")

from rembg import remove

def transparent_clothes():
    if not os.path.exists(CLOTHES_GRID): return
    img = Image.open(CLOTHES_GRID)
    print("Using rembg to remove background...")
    img = remove(img)
    img.save("test_rembg_output.png")
    print("Success")

transparent_clothes()
