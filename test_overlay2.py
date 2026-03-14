from PIL import Image, ImageDraw
import os

PLAYER_IMG = "assets/player_v10/front.png"
TOP_IMG = "assets/v10_items/top_1.png"
TRACK_IMG = "assets/v10_items/tracksuit_1.png"

base = Image.open(PLAYER_IMG).convert("RGBA")
base_w, base_h = base.size # 143x285

cfg = {
    "top": {"width_ratio": 0.58, "y_anchor": 0.48},     # 143 * 0.58 = 83px wide
    "bottom": {"width_ratio": 0.55, "y_anchor": 0.61},
    "tracksuit": {"width_ratio": 0.65, "y_anchor": 0.48},
    "party_dress": {"width_ratio": 0.85, "y_anchor": 0.48},
    "hair": {"width_ratio": 0.90, "y_anchor": 0.15},
    "hat": {"width_ratio": 1.0, "y_anchor": 0.05},
    "shoes_snekers": {"width_ratio": 0.45, "y_anchor": 0.92}
}

def draw_item(img_path, cat, out, b_w, b_h, x_offset=0):
    if not os.path.exists(img_path): return out
    item = Image.open(img_path).convert("RGBA")
    c = cfg[cat]
    iw = int(b_w * c["width_ratio"])
    ih = int(item.height * (iw / item.width))
    item = item.resize((iw, ih), Image.Resampling.LANCZOS)
    
    cx = b_w // 2 + x_offset
    cy_y = int(b_h * c["y_anchor"])
    
    # logic matching game.py
    # if top, midtop at cy_y. For others, midtop or center?
    if cat in ["top", "tracksuit", "party_dress"]:
        # midtop
        tx = cx - iw // 2
        ty = cy_y
    elif cat in ["bottom"]:
        tx = cx - iw // 2
        ty = cy_y
    elif cat in ["hair"]:
        tx = cx - iw // 2
        ty = cy_y - ih // 2 # center
        
    final = out.copy()
    final.paste(item, (tx, ty), item)
    return final

out1 = draw_item(TOP_IMG, "top", base, base_w, base_h)
out2 = draw_item(TRACK_IMG, "tracksuit", base, base_w, base_h)
out1.save("/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3/debug_top.png")
out2.save("/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3/debug_track.png")
print("Saved overlays")
