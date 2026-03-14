from PIL import Image, ImageDraw
import json
import os
import colorsys

BRAIN_DIR = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"
CLOTHES_GRID = os.path.join(BRAIN_DIR, "v10_clothes_grid_1773460054645.png")
OUT_DIR = "assets/v10_items"

def remove_background(img, threshold=240):
    """
    More aggressive background removal: any pixel where R,G,B are all > threshold
    becomes transparent. Also tries to remove shadows (grey pixels).
    """
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    
    # 1. Flood fill from corners with high threshold to remove continuous white
    for seed in [(0,0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]:
        if seed[0] < w and seed[1] < h:
            ImageDraw.floodfill(img, seed, (0,0,0,0), thresh=80)
            
    # 2. Manual pass to clean up any remaining near-white or grey shadow pixels
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # If pixel is very bright (near white)
                if r > threshold and g > threshold and b > threshold:
                    pixels[x, y] = (0,0,0,0)
                # If pixel is a grey shadow (r,g,b are similar and bright but not white, typically > 200)
                # We can check color saturation
                elif r > 200 and g > 200 and b > 200:
                    diff = max(r,g,b) - min(r,g,b)
                    if diff < 15: # It's a shade of grey
                        pixels[x, y] = (0,0,0,0)
    return img

img = Image.open(CLOTHES_GRID).convert("RGBA")

# Cell dimensions: 4 cols, 5 rows
cols, rows = 4, 5
w, h = img.size
cw, ch = w / float(cols), h / float(rows)

# Let's just process the first cell (the pink dress) and print its bbox 
# and the 4th cell (green tracksuit) which is the second row last cols? 
# Wait, let's process the green tracksuit
cell_tracksuit = img.crop((int(3*cw), 0, int(4*cw), int(ch)))

cell_tracksuit = remove_background(cell_tracksuit, threshold=235)
bbox = cell_tracksuit.getbbox()
print("Tracksuit bbox:", bbox)
if bbox:
    cropped = cell_tracksuit.crop(bbox)
    cropped.save("test_extract_tracksuit.png")
    print(f"Saved cropped tracksuit. Size: {cropped.size}")

