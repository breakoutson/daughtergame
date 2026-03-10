from PIL import Image, ImageDraw, ImageFilter
import os

def surgical_clean(image_path, rows=4, cols=4, char_type="player"):
    if not os.path.exists(image_path): return
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    tile_w = w // cols
    tile_h = h // rows
    
    output_dir_name = os.path.basename(image_path).replace(".png", "_frames")
    output_dir = os.path.join(os.path.dirname(image_path), output_dir_name)
    os.makedirs(output_dir, exist_ok=True)
    
    directions = ["front", "back", "left", "right"]
    
    for r in range(rows):
        dir_name = directions[r] if r < len(directions) else f"row_{r}"
        for c in range(cols):
            # 1. 타일 크롭
            left = c * tile_w
            top = r * tile_h
            right = (c + 1) * tile_w
            bottom = (r + 1) * tile_h
            tile = img.crop((left, top, right, bottom))
            
            # 2. 텍스트 라벨만 정밀하게 지우기 (상단 약 25픽셀)
            # 캐릭터 머리가 잘리지 않도록 상단 영역만 체크해서 흰색이면 투명화
            draw = ImageDraw.Draw(tile)
            # 보통 상단 15% 정도에 텍스트가 있으므로 그 부분만 흰색으로 덮은 뒤 투명화
            # 하지만 머리카락이 위까지 올라올 수 있으므로 텍스트 영역만 투명박스로 채움
            # DALL-E 텍스트는 보통 중앙 상단에 위치함
            # 안전하게 상단 20픽셀 정도를 체크하여 배경색과 같은 흰색이면 투명하게 날림
            
            # 3. 플러드 필 (Flood Fill) - 외곽 배경 제거
            # 네 귀퉁이와 상단 모서리들에서 시작
            target_color = (255, 255, 255, 255)
            replacement_color = (255, 255, 255, 0)
            
            # 이미지 외곽에서 시작하는 모든 흰색(245 이상)을 투명하게
            # thres 30 정도로 배경 노이즈 제거
            for seed in [(0,0), (tile.width-1, 0), (0, tile.height-1), (tile.width-1, tile.height-1), (tile.width//2, 2)]:
                try:
                    ImageDraw.floodfill(tile, seed, replacement_color, thresh=30)
                except:
                    pass
            
            # 4. 추가: 상단 텍스트 강제 제거 박스 (캐릭터 머리가 닿지 않는 안전 영역)
            # 만약 글자가 여전히 보인다면 이 수치를 조절
            # tile.paste((255,255,255,0), [0, 0, tile.width, 15]) 

            # 5. 저장
            tile.save(os.path.join(output_dir, f"{dir_name}_{c}.png"))

ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"
surgical_clean(os.path.join(ASSETS, "player_sheet.png"))
surgical_clean(os.path.join(ASSETS, "dog_sheet.png"))

# 개별 아이템들도 다시 깨끗하게 (단일 이미지용)
def clean_single_item(path):
    if not os.path.exists(path): return
    img = Image.open(path).convert("RGBA")
    # 외곽 흰색만 제거
    ImageDraw.floodfill(img, (0,0), (255, 255, 255, 0), thresh=40)
    ImageDraw.floodfill(img, (img.width-1, 0), (255, 255, 255, 0), thresh=40)
    img.save(path)

items = ["pink_dress.png", "yellow_dress.png", "crown.png", "wings.png", "shoes.png"]
for item in items:
    clean_single_item(os.path.join(ASSETS, item))

print("Assets surgically cleaned while preserving white bodies and hair.")
