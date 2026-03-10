from PIL import Image, ImageDraw
import os

def slice_and_clean(image_path, output_dir, coords):
    if not os.path.exists(image_path): return
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(image_path).convert("RGBA")
    
    for name, box in coords.items():
        tile = img.crop(box)
        # 강력한 배경 제거
        data = tile.getdata()
        new_data = []
        for item in data:
            # 흰색 계열 (240 이상) 또는 배경 노이즈 제거
            if item[0] > 230 and item[1] > 230 and item[2] > 230:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        tile.putdata(new_data)
        tile.save(os.path.join(output_dir, f"{name}.png"))

ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"

# 캐릭터 수동 슬라이싱 (DALL-E 생성물 위치에 최적화)
char_coords = {
    "front": (148, 66, 434, 477),
    "back": (558, 66, 844, 477),
    "left": (148, 516, 434, 927),
    "right": (558, 516, 844, 927)
}
slice_and_clean(os.path.join(ASSETS, "char_all.png"), os.path.join(ASSETS, "player_clean"), char_coords)

# 강아지 수동 슬라이싱
dog_coords = {
    "idle": (60, 80, 420, 520),
    "walk": (520, 80, 880, 520),
    "sleep": (180, 580, 820, 920)
}
slice_and_clean(os.path.join(ASSETS, "dog_all.png"), os.path.join(ASSETS, "dog_clean"), dog_coords)

print("Surgery assets prepared cleanly!")
