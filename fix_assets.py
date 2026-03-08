from PIL import Image, ImageDraw
import os

def clean_sprite_with_floodfill(image_path, text_crop_height=30):
    if not os.path.exists(image_path): return
    
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    
    # 1. 상단 텍스트 라벨 잘라내기 (있는 경우에만 적용되도록 여유있게)
    # 하지만 슬라이싱 할 때 이미 조절할 것이므로 여기서는 투명도 처리에 집중합니다.

    # 2. 배경 투명화 (Flood Fill 방식)
    # 이미지의 네 귀퉁이에서 시작해서 하얀색 배경을 투명색으로 채웁니다.
    # 이렇게 하면 하얀색 강아지 몸 안쪽은 지워지지 않습니다.
    target_color = (255, 255, 255, 255) # 순백색
    replacement_color = (255, 255, 255, 0) # 투명색
    
    # 사방에서 채우기 시작
    seeds = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1)]
    for seed in seeds:
        try:
            ImageDraw.floodfill(img, seed, replacement_color, thresh=10)
        except:
            pass

    img.save(image_path)
    print(f"Cleaned with floodfill: {image_path}")

# 슬러이싱 코드도 수정 (텍스트 라벨 무시)
def slice_spritesheet_refined(sheet_path, output_dir, rows, cols):
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
            # 텍스트 라벨이 보통 윗부분에 있으므로, 타일의 윗부분 15% 정도를 아예 잘라냄
            # 캐릭터 위치에 따라 조정 필요
            left = c * tile_w
            top = r * tile_h + (tile_h // 6) # 윗부분 생략
            right = (c + 1) * tile_w
            bottom = (r + 1) * tile_h
            
            tile = img.crop((left, top, right, bottom))
            
            # 여기서도 한 번 더 플러드 필
            ImageDraw.floodfill(tile, (0, 0), (255, 255, 255, 0), thresh=20)
            ImageDraw.floodfill(tile, (tile.width-1, 0), (255, 255, 255, 0), thresh=20)
            
            tile.save(os.path.join(output_dir, f"{dir_name}_{c}.png"))

ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"
# 1. 플레이어 슬라이싱 (텍스트 제거 포함)
slice_spritesheet_refined(os.path.join(ASSETS, "player_sheet.png"), os.path.join(ASSETS, "player_frames"), 4, 4)
# 2. 강아지 슬라이싱
slice_spritesheet_refined(os.path.join(ASSETS, "dog_sheet.png"), os.path.join(ASSETS, "dog_frames"), 4, 4)
print("Assets Re-processed Successfully!")
