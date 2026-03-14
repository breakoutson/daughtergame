from PIL import Image
import os

def to_shorts(in_path, out_path):
    if not os.path.exists(in_path): return
    img = Image.open(in_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    
    # Skin color to replace with
    skin_color = (255, 224, 204, 255)
    
    # Simple heuristic: Replace white pixels in the lower half of arms and legs with skin color
    # We will just traverse and replace pixels that are nearly white
    for y in range(int(h * 0.6), int(h * 0.95)):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 100:
                # If it's a "white-ish" pixel (pajamas)
                if r > 210 and g > 210 and b > 210:
                    # check if not part of a distinct border (simple hack: just replace all white)
                    pixels[x, y] = skin_color
                    
    img.save(out_path)

os.makedirs("assets/player_v10", exist_ok=True)
to_shorts("assets/player_v6/front.png", "assets/player_v10/front.png")
to_shorts("assets/player_v6/back.png", "assets/player_v10/back.png")
to_shorts("assets/player_v6/side_l.png", "assets/player_v10/side_l.png")
to_shorts("assets/player_v6/side_r.png", "assets/player_v10/side_r.png")

print("Created V10 short-sleeve/shorts character base.")
