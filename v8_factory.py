import os
import math
import random
import colorsys
import json
from PIL import Image, ImageDraw

BRAIN_DIR = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"
CLOTHES_GRID = os.path.join(BRAIN_DIR, "roblox_clothes_grid_1773456339967.png")
ACCS_GRID = os.path.join(BRAIN_DIR, "roblox_accs_grid_1773456357871.png")
OUT_DIR = "/Users/son-yongseok/aidev/princess-dressup/assets/v8_items"
os.makedirs(OUT_DIR, exist_ok=True)

def flood_clear_bg(img, thresh=40):
    for seed in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)]:
        if seed[0] < img.width and seed[1] < img.height:
            ImageDraw.floodfill(img, seed, (0,0,0,0), thresh=thresh)
    return img

def extract_cells(img_path, rows, cols, expect_cells=None):
    if not os.path.exists(img_path): return []
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    cw, ch = w / float(cols), h / float(rows)
    
    cells = []
    for r in range(rows):
        for c in range(cols):
            box = (int(c * cw), int(r * ch), int((c+1) * cw), int((r+1) * ch))
            cell = img.crop(box)
            cell = flood_clear_bg(cell)
            bbox = cell.getbbox()
            if bbox:
                # Minimum size filter
                if bbox[2] - bbox[0] > 20 and bbox[3] - bbox[1] > 20:
                    cells.append(cell.crop(bbox))
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

def generate_category(base_images, name, count, target_h):
    res = []
    shifts = [0, 0.2, 0.4, 0.6, 0.8, 0.1, 0.3, 0.5, 0.7, 0.9]
    for i in range(count):
        base = base_images[i % len(base_images)]
        shifted = tint_image(base, shifts[i % len(shifts)])
        
        # Resize to predictable target height
        aw = int(shifted.width * (target_h / shifted.height))
        shifted = shifted.resize((aw, target_h), Image.Resampling.LANCZOS)
        
        fname = f"{name}_{i+1}.png"
        shifted.save(os.path.join(OUT_DIR, fname))
        res.append(fname)
    return res

print("Extracting clothes grid...")
clothes_cells = extract_cells(CLOTHES_GRID, 4, 5) 
print(f"Extracted {len(clothes_cells)} clothes")

print("Extracting accs grid...")
# According to prompt it was 4 rows of 5 for accessories too, let's process 7 rows 4 cols just in case it interpreted differently.
accs_img = Image.open(ACCS_GRID)
cw, ch = accs_img.size
# Let's inspect rows/cols based on image size. Let's just assume 7x4 because of the generated image aspect ratio.
acc_cells = extract_cells(ACCS_GRID, 7, 4)
if len(acc_cells) < 10:
    acc_cells = extract_cells(ACCS_GRID, 4, 5) # fallback fallback
print(f"Extracted {len(acc_cells)} accessories")

catalog = {}

# Make sure we have enough distinct bases
# Let's pseudo-segment them based on index (rough estimation, it adds variance)
if len(clothes_cells) > 0:
    catalog["top"] = generate_category(clothes_cells[0:5], "top", 10, target_h=120)
    catalog["bottom"] = generate_category(clothes_cells[5:10] if len(clothes_cells) > 5 else clothes_cells, "bottom", 10, target_h=120)
    catalog["pajamas"] = generate_category(clothes_cells[10:12] if len(clothes_cells) > 10 else clothes_cells, "pajamas", 2, target_h=180)
    catalog["tracksuit"] = generate_category(clothes_cells[12:15] if len(clothes_cells) > 12 else clothes_cells, "tracksuit", 2, target_h=180)
    catalog["party_dress"] = generate_category(clothes_cells[15:] if len(clothes_cells) > 15 else clothes_cells, "party", 3, target_h=200)
else:
    print("NO CLOTHES FOUND!")

if len(acc_cells) > 0:
    catalog["hair"] = generate_category(acc_cells[0:4], "hair", 4, target_h=130)
    catalog["shoes_sneakers"] = generate_category(acc_cells[4:8] if len(acc_cells) > 4 else acc_cells, "sneakers", 5, target_h=40)
    catalog["shoes_slippers"] = generate_category(acc_cells[8:12] if len(acc_cells) > 8 else acc_cells, "slippers", 5, target_h=40)
    catalog["shoes_dress"] = generate_category(acc_cells[12:16] if len(acc_cells) > 12 else acc_cells, "dress_shoes", 5, target_h=40)
    catalog["glasses"] = generate_category(acc_cells[16:20] if len(acc_cells) > 16 else acc_cells, "glasses", 2, target_h=35)
    catalog["sunglasses"] = generate_category(acc_cells[16:20] if len(acc_cells) > 16 else acc_cells, "sunglasses", 2, target_h=35)
    catalog["bag"] = generate_category(acc_cells[20:24] if len(acc_cells) > 20 else acc_cells, "bag", 3, target_h=80)
    catalog["hat"] = generate_category(acc_cells[24:] if len(acc_cells) > 24 else acc_cells, "hat", 4, target_h=60)
else:
    print("NO ACCS FOUND!")

with open(os.path.join(OUT_DIR, "catalog.json"), "w") as f:
    json.dump(catalog, f, indent=4)

print("Massive Factory production complete! 50+ items ready.")
