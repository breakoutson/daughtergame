from PIL import Image, ImageDraw
import os

def floodfill_process_dog(image_path, rows=4, cols=4):
    if not os.path.exists(image_path): return
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    tile_w = w // cols
    tile_h = h // rows
    
    output_dir = os.path.join(os.path.dirname(image_path), "dog_sheet_frames")
    os.makedirs(output_dir, exist_ok=True)
    
    directions = ["front", "back", "left", "right"]
    for r in range(rows):
        for c in range(cols):
            # 타일 자르기 (상단 라벨 피해서)
            left = c * tile_w
            top = int(r * tile_h + tile_h * 0.15)
            right = (c + 1) * tile_w
            bottom = (r + 1) * tile_h
            tile = img.crop((left, top, right, bottom))
            
            # 플러드 필로 외곽 흰색만 제거
            # 사방 귀퉁이에서 투명색 채우기
            for seed in [(0, 0), (tile.width-1, 0), (0, tile.height-1), (tile.width-1, tile.height-1)]:
                ImageDraw.floodfill(tile, seed, (255, 255, 255, 0), thresh=30)
            
            tile.save(os.path.join(output_dir, f"{directions[r]}_{c}.png"))

ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"
floodfill_process_dog(os.path.join(ASSETS, "dog_sheet.png"))
print("Dog assets fixed with floodfill (White body preserved).")
