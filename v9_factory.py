import os
import math
import random
import colorsys
import json
from PIL import Image, ImageDraw, ImageEnhance

BRAIN_DIR = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"
BASE_IMG = os.path.join(BRAIN_DIR, "chibi_base_shorts_1773458053906.png")
CLOTHES_GRID = os.path.join(BRAIN_DIR, "chibi_clothes_grid_1773458071774.png")
ACCS_GRID = os.path.join(BRAIN_DIR, "chibi_accs_grid_1773458087369.png")
OUT_DIR = "/Users/son-yongseok/aidev/princess-dressup/assets/v9_items"
PLAYER_DIR = "/Users/son-yongseok/aidev/princess-dressup/assets/v9_player"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PLAYER_DIR, exist_ok=True)

def flood_clear_bg(img, thresh=40):
    for seed in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1), (img.width//2, 0)]:
        if seed[0] < img.width and seed[1] < img.height:
            ImageDraw.floodfill(img, seed, (0,0,0,0), thresh=thresh)
    return img

def extract_cells(img_path, target_count=20):
    if not os.path.exists(img_path): return []
    img = Image.open(img_path).convert("RGBA")
    
    # Try 5x4 or 4x5
    best_cells = []
    for (rows, cols) in [(5, 4), (4, 5), (5, 5), (6, 5), (5, 6)]:
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
    return best_cells

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

# 1. Process Player Base
if os.path.exists(BASE_IMG):
    bimg = Image.open(BASE_IMG).convert("RGBA")
    bimg = flood_clear_bg(bimg, thresh=40)
    # the image has 4 poses in a row. Let's slice into 4 cols
    w, h = bimg.size
    cw = w / 4.0
    poses = []
    for c in range(4):
        box = (int(c * cw), 0, int((c+1) * cw), h)
        cell = bimg.crop(box)
        bbox = cell.getbbox()
        if bbox:
            poses.append(cell.crop(bbox))
    
    # Usually: front, back, side_l/r. Let's assume order from prompt: Front, Back, Left, Right
    if len(poses) >= 4:
        poses[0].save(os.path.join(PLAYER_DIR, "front.png"))
        poses[1].save(os.path.join(PLAYER_DIR, "back.png"))
        poses[2].save(os.path.join(PLAYER_DIR, "side_l.png"))
        poses[3].save(os.path.join(PLAYER_DIR, "side_r.png"))

# 2. Process Clothes & Accs
clothes = extract_cells(CLOTHES_GRID, 20)
accs = extract_cells(ACCS_GRID, 20)

print(f"Extracted {len(clothes)} clothes and {len(accs)} accs.")

catalog = {}
def gen(items, cat, count, anchor_type, scale_factor=1.0):
    res = []
    shifts = [0, 0.4, 0.1, 0.7, 0.3, 0.8, 0.2, 0.5, 0.9, 0.6]
    for i in range(count):
        if not items: break
        base = items[i % len(items)]
        shifted = tint_image(base, shifts[i % len(shifts)])
        
        # We don't resize height blindly anymore because that destroys aspect ratios.
        # We only apply a unified scaling factor to preserve proportions perfectly.
        # Character is ~220px. Base items are from 1024/4=256px boxes.
        nw = int(shifted.width * scale_factor)
        nh = int(shifted.height * scale_factor)
        if nw > 0 and nh > 0:
            shifted = shifted.resize((nw, nh), Image.Resampling.LANCZOS)
            
        fname = f"{cat}_{i+1}.png"
        shifted.save(os.path.join(OUT_DIR, fname))
        res.append({"file": fname, "anchor_type": anchor_type})
    return res

# Assign items based on visual grid structure
if len(clothes) > 0:
    # Scale factor tweak: clothes need to fit the new base body. Let's say scale_factor=0.6
    sf = 0.55
    catalog["top"] = gen(clothes[0:5], "top", 10, "top_center", sf)
    catalog["bottom"] = gen(clothes[5:10], "bottom", 10, "top_center", sf)
    catalog["tracksuit"] = gen(clothes[10:15], "tracksuit", 2, "top_center", sf)
    catalog["party_dress"] = gen(clothes[15:], "party", 3, "top_center", sf)
    catalog["pajamas"] = gen(clothes[0:2], "pajamas", 2, "top_center", sf)

if len(accs) > 0:
    sf = 0.5
    catalog["hair"] = gen(accs[0:4], "hair", 4, "top_center", sf)
    catalog["glasses"] = gen(accs[4:8], "glasses", 2, "center", sf)
    catalog["sunglasses"] = gen(accs[4:8], "sunglasses", 2, "center", sf)
    catalog["bag"] = gen(accs[8:12], "bag", 3, "center", sf)
    catalog["hat"] = gen(accs[12:16], "hat", 4, "bottom_center", sf)
    catalog["shoes_sneakers"] = gen(accs[16:], "sneakers", 5, "bottom_center", sf)
    catalog["shoes_slippers"] = gen(accs[16:], "slippers", 5, "bottom_center", sf)
    catalog["shoes_dress"] = gen(accs[16:], "dress_shoes", 5, "bottom_center", sf)

with open(os.path.join(OUT_DIR, "catalog.json"), "w") as f:
    json.dump(catalog, f, indent=4)

print("V9 Factory complete!")
