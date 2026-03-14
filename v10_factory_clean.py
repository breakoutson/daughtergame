from PIL import Image, ImageDraw
import json
import os
import colorsys

BRAIN_DIR = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"
CLOTHES_GRID = os.path.join(BRAIN_DIR, "v10_clothes_grid_1773460054645.png")
ACCS_GRID = os.path.join(BRAIN_DIR, "v10_accs_grid_1773460073340.png")
OUT_DIR = "/Users/son-yongseok/aidev/princess-dressup/assets/v10_items"

def get_components(img_path):
    # 1. Load and remove white bg globally
    if not os.path.exists(img_path): return []
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    pixels = img.load()
    
    # Simple color keying + floodfill
    # First flood fill
    for seed in [(0,0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1)]:
        if seed[0] < w and seed[1] < h:
            ImageDraw.floodfill(img, seed, (0,0,0,0), thresh=80)
            
    # Remove shadows and remaining white
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0:
                if r > 230 and g > 230 and b > 230:
                    pixels[x, y] = (0,0,0,0)
                elif r > 180 and g > 180 and b > 180 and max(r,g,b)-min(r,g,b) < 15:
                    pixels[x, y] = (0,0,0,0)

    # 2. Find bounding boxes of all disjoint components
    # We can do this by using getbbox() iteratively or simply scanning
    # But PIL doesn't have an easy connected components.
    # Instead, we can divide into 4 cols, 5 rows safely NOW since we've removed the background.
    # After bg removal, the objects are floating. We can use the cells, but instead
    # of just cropping the cell, we crop the cell THEN getbbox() to isolate the item center!
    
    cells = []
    cw, ch = w / 4.0, h / 5.0
    for r in range(5):
        for c in range(4):
            # Give a little padding to the cell to avoid cutting items that spill over slightly
            pad = 10
            left = max(0, int(c * cw) - pad)
            top = max(0, int(r * ch) - pad)
            right = min(w, int((c+1) * cw) + pad)
            bottom = min(h, int((r+1) * ch) + pad)
            
            cell = img.crop((left, top, right, bottom))
            bbox = cell.getbbox()
            
            if bbox and (bbox[2] - bbox[0] > 20) and (bbox[3] - bbox[1] > 20):
                # We have the precise boundary!
                cropped = cell.crop(bbox)
                cells.append(cropped)
    return cells

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

clothes = get_components(CLOTHES_GRID)
accs = get_components(ACCS_GRID)

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

print("V10 Clean Extract Complete.")
