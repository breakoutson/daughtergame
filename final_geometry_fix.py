from PIL import Image, ImageDraw
import os

def precise_crop_and_scale(image_path, output_path, target_height):
    if not os.path.exists(image_path): return
    img = Image.open(image_path).convert("RGBA")
    
    # 1. 완벽한 배경 제거 (색상 오차 50까지 허용)
    for seed in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)]:
        ImageDraw.floodfill(img, seed, (0, 0, 0, 0), thresh=50)
    
    # 2. 내용물만 타이트하게 크롭 (여백 제거)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    # 3. 목표 높이에 맞춰 리사이즈 (캐릭터 비율 유지)
    aspect = img.width / img.height
    target_width = int(target_height * aspect)
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    img.save(output_path)
    print(f"Surgery Finished: {output_path} (Size: {target_width}x{target_height})")

DIR = "/Users/son-yongseok/aidev/princess-dressup/assets"
BRAIN = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"

# 캐릭터 높이: 200px (전체 750px의 약 1/4)
precise_crop_and_scale(os.path.join(BRAIN, "char_front_clean_1773147015980.png"), os.path.join(DIR, "player_fixed/front.png"), 200)
precise_crop_and_scale(os.path.join(BRAIN, "char_back_clean_1773147032034.png"), os.path.join(DIR, "player_fixed/back.png"), 200)
precise_crop_and_scale(os.path.join(BRAIN, "char_side_clean_1773147071178.png"), os.path.join(DIR, "player_fixed/side.png"), 200)

# 강아지 높이: 80px (캐릭터의 약 1/3)
precise_crop_and_scale(os.path.join(BRAIN, "maltese_idle_clean_1773147087027.png"), os.path.join(DIR, "dog_fixed/idle.png"), 80)

# 옷 & 액세서리 (캐릭터 크기에 맞춰 미리 조정)
precise_crop_and_scale(os.path.join(DIR, "pink_dress.png"), os.path.join(DIR, "pink_dress_fixed.png"), 120)
precise_crop_and_scale(os.path.join(DIR, "yellow_dress.png"), os.path.join(DIR, "yellow_dress_fixed.png"), 120)
precise_crop_and_scale(os.path.join(DIR, "wings.png"), os.path.join(DIR, "wings_fixed.png"), 150)
precise_crop_and_scale(os.path.join(DIR, "crown.png"), os.path.join(DIR, "crown_fixed.png"), 40)
