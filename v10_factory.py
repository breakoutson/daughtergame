import os
import random
import colorsys
import json
from PIL import Image, ImageDraw

BRAIN_DIR = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"
CLOTHES_GRID = os.path.join(BRAIN_DIR, "v10_clothes_grid_1773460054645.png")
ACCS_GRID = os.path.join(BRAIN_DIR, "v10_accs_grid_1773460073340.png")
OUT_DIR = "/Users/son-yongseok/aidev/princess-dressup/assets/v10_items"
os.makedirs(OUT_DIR, exist_ok=True)

def flood_clear_bg(img, thresh=40):
    for seed in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1), (img.width//2, 0)]:
        if seed[0] < img.width and seed[1] < img.height:
            ImageDraw.floodfill(img, seed, (0,0,0,0), thresh=thresh)
    return img

def extract_cells(img_path, target_count=20):
    if not os.path.exists(img_path): return []
    img = Image.open(img_path).convert("RGBA")
    
    # Grid is 4 cols, 5 rows usually
    for (cols, rows) in [(4, 5), (5, 4)]:
        w, h = img.size
        cw, ch = w / float(cols), h / float(rows)
        cells = []
        for r in range(rows):
            for c in range(cols):
                box = (int(c * cw), int(r * ch), int((c+1) * cw), int((r+1) * ch))
                cell = img.crop(box)
                cell = flood_clear_bg(cell, thresh=20)
                bbox = cell.getbbox()
                if bbox and (bbox[2] - bbox[0] > 20) and (bbox[3] - bbox[1] > 20):
                    cells.append(cell.crop(bbox))
        if len(cells) >= target_count:
            return cells
    return []

def tint_image(img, hue_shift):
    if hue_shift == 0: return img.copy()
    out = Image.new("RGBA", img.size)
    pixels = img.load()
    out_pixels = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a > 0:
                h, s, v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
                nh = (h + hue_shift) % 1.0
                nr, ng, nb = colorsys.hsv_to_rgb(nh, s, v)
                out_pixels[x, y] = (int(nr*255), int(ng*255), int(nb*255), a)
            else:
                out_pixels[x, y] = (0,0,0,0)
    return out

clothes = extract_cells(CLOTHES_GRID, 20)
accs = extract_cells(ACCS_GRID, 20)

print(f"Extracted {len(clothes)} clothes and {len(accs)} accs.")

catalog = {}
def gen(items, cat, count, cat_type):
    res = []
    shifts = [0, 0.4, 0.1, 0.7, 0.3, 0.8, 0.2, 0.5, 0.9, 0.6]
    for i in range(count):
        if not items: break
        base = items[i % len(items)]
        shifted = tint_image(base, shifts[i % len(shifts)])
        
        fname = f"{cat}_{i+1}.png"
        shifted.save(os.path.join(OUT_DIR, fname))
        
        # We save metadata for game.py layout engine
        res.append({
            "file": fname,
            "type": cat_type, 
            "original_width": shifted.width,
            "original_height": shifted.height
        })
    return res

if len(clothes) > 0:
    catalog["top"] = gen(clothes[0:4], "top", 10, "top")
    catalog["bottom"] = gen(clothes[4:8], "bottom", 10, "bottom")
    catalog["party_dress"] = gen(clothes[8:12], "party", 3, "full_body")
    catalog["tracksuit"] = gen(clothes[12:16], "tracksuit", 2, "full_body")
    catalog["pajamas"] = gen(clothes[16:20], "pajamas", 2, "full_body")

if len(accs) > 0:
    catalog["hair"] = gen(accs[0:4], "hair", 4, "head")
    catalog["hat"] = gen(accs[12:16], "hat", 4, "head_top")
    catalog["glasses"] = gen(accs[4:6], "glasses", 2, "face")
    catalog["sunglasses"] = gen(accs[6:8], "sunglasses", 2, "face")
    catalog["bag"] = gen(accs[8:12], "bag", 3, "hand")
    catalog["shoes_sneakers"] = gen(accs[16:20], "sneakers", 5, "feet")
    catalog["shoes_slippers"] = gen(accs[16:20], "slippers", 5, "feet")
    catalog["shoes_dress"] = gen(accs[16:20], "dress_shoes", 5, "feet")

with open(os.path.join(OUT_DIR, "catalog.json"), "w") as f:
    json.dump(catalog, f, indent=4)

print("V10 Assets Created")
