from PIL import Image, ImageDraw, ImageChops
import os

def process_image_perfectly(image_path, is_spritesheet=False, rows=4, cols=4, hide_label_percent=0.15):
    if not os.path.exists(image_path): return
    
    img = Image.open(image_path).convert("RGBA")
    
    # 1. 배경 완벽 제거 (순백색 근처를 투명으로)
    # 이미지의 외곽에서부터 투명화 처리
    def make_transparent(target_img):
        data = target_img.getdata()
        new_data = []
        for item in data:
            # 흰색(240 이상)을 투명하게
            if item[0] > 235 and item[1] > 235 and item[2] > 235:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        target_img.putdata(new_data)
        return target_img

    if not is_spritesheet:
        img = make_transparent(img)
        img.save(image_path)
    else:
        # 스프라이트 시트인 경우 슬라이싱하면서 개별 처리
        w, h = img.size
        tile_w = w // cols
        tile_h = h // rows
        output_dir = os.path.join(os.path.dirname(image_path), os.path.basename(image_path).replace(".png", "_frames"))
        os.makedirs(output_dir, exist_ok=True)
        
        directions = ["front", "back", "left", "right"]
        
        for r in range(rows):
            dir_name = directions[r] if r < len(directions) else f"row_{r}"
            for c in range(cols):
                # 텍스트 라벨(WALK FRONT 등) 피해서 크롭 (상단 15% 버림)
                left = c * tile_w
                top = int(r * tile_h + tile_h * hide_label_percent)
                right = (c + 1) * tile_w
                bottom = (r + 1) * tile_h
                
                tile = img.crop((left, top, right, bottom))
                
                # 투명화
                tile = make_transparent(tile)
                
                # 실제 이미지 내용만 있는 부분으로 한 번 더 타이트하게 크롭 (잘림 방지)
                # 바운딩 박스를 이용해서 캐릭터만 남김
                bbox = tile.getbbox()
                if bbox:
                    # 캐릭터가 잘리지 않도록 여백을 두고 저장하거나, 
                    # 일관된 크기를 유지하기 위해 원본 타일 크기를 유지하면서 내용물만 정렬할 수도 있음
                    # 여기서는 일단 투명화된 타일을 그대로 저장
                    tile.save(os.path.join(output_dir, f"{dir_name}_{c}.png"))

ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"

# 강아지 이미지 처리 (스프라이트 시트가 아닌 단일 이미지인 경우도 고려)
process_image_perfectly(os.path.join(ASSETS, "dog_sheet.png"), is_spritesheet=True)
process_image_perfectly(os.path.join(ASSETS, "player_sheet.png"), is_spritesheet=True, hide_label_percent=0.18)

# 기존 개별 아이템들 다시 처리
items = ["character.png", "bunny.png", "chest.png", "pink_dress.png", "yellow_dress.png", "crown.png", "shoes.png", "wings.png"]
for item in items:
    process_image_perfectly(os.path.join(ASSETS, item))

print("All assets processed with perfect transparency and cropping.")
