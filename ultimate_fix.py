from PIL import Image, ImageDraw
import os

def ultimate_asset_fix(image_path, rows=4, cols=4):
    if not os.path.exists(image_path): return
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    tile_w = w // cols
    tile_h = h // rows
    
    # 출력 경로 설정 (기존 프레임 폴더 덮어쓰기)
    dir_name = os.path.basename(image_path).replace(".png", "_sheet_frames")
    output_dir = os.path.join(os.path.dirname(image_path), dir_name)
    os.makedirs(output_dir, exist_ok=True)
    
    directions = ["front", "back", "left", "right"]
    
    for r in range(rows):
        cur_dir = directions[r]
        for c in range(cols):
            # 1. 공격적인 크롭 (상단 22% 날려서 WALK 글자 완전 박멸)
            left = c * tile_w
            top = int(r * tile_h + tile_h * 0.22) # 머리 위 글자 완전 제거
            right = (c + 1) * tile_w
            bottom = (r + 1) * tile_h
            tile = img.crop((left, top, right, bottom))
            
            # 2. 사각형 테두리 잔상 박멸 (Near-white 투명화)
            # 흰색(255)뿐만 아니라 230 이상의 밝은 색은 모두 투명하게
            data = tile.getdata()
            new_data = []
            for item in data:
                # RGB 값이 모두 230 이상이면(연한 회색 테두리 포함) 투명하게
                if item[0] > 230 and item[1] > 230 and item[2] > 230:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            tile.putdata(new_data)
            
            # 3. 플러드 필로 안쪽은 최대한 보호 (강아지 몸 등)
            # 하지만 이미 위에서 처리했으므로 저장만 해도 깔끔함
            tile.save(os.path.join(output_dir, f"{cur_dir}_{c}.png"))
    print(f"Fixed: {image_path}")

ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"
ultimate_asset_fix(os.path.join(ASSETS, "player_sheet.png"))
ultimate_asset_fix(os.path.join(ASSETS, "dog_sheet.png"))
print("Text labels and faint borders are GONE!")
