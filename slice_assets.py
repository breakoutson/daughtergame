import pygame
import os
from PIL import Image

def slice_spritesheet(sheet_path, output_dir, rows, cols):
    if not os.path.exists(sheet_path): return
    os.makedirs(output_dir, exist_ok=True)
    
    img = Image.open(sheet_path).convert("RGBA")
    w, h = img.size
    tile_w = w // cols
    tile_h = h // rows
    
    directions = ["front", "back", "left", "right"]
    
    for r in range(rows):
        dir_name = directions[r] if r < len(directions) else f"row_{r}"
        for c in range(cols):
            left = c * tile_w
            top = r * tile_h
            right = (c + 1) * tile_w
            bottom = (r + 1) * tile_h
            
            tile = img.crop((left, top, right, bottom))
            
            # 배경 투명화 처리
            datas = tile.getdata()
            new_data = []
            for item in datas:
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            tile.putdata(new_data)
            
            tile.save(os.path.join(output_dir, f"{dir_name}_{c}.png"))

ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"
slice_spritesheet(os.path.join(ASSETS, "player_sheet.png"), os.path.join(ASSETS, "player_frames"), 4, 4)
slice_spritesheet(os.path.join(ASSETS, "dog_sheet.png"), os.path.join(ASSETS, "dog_frames"), 4, 4)
print("Sprites sliced and cleaned!")
