from PIL import Image, ImageDraw
import os

def final_clean(path):
    if not os.path.exists(path): return
    img = Image.open(path).convert("RGBA")
    
    # 사방 끝 포인트에서 플러드 필로 배경 투명화 (threshold 높여서 완벽 박멸)
    for seed in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)]:
        ImageDraw.floodfill(img, seed, (255, 255, 255, 0), thresh=45)
    
    img.save(path)

DIR = "/Users/son-yongseok/aidev/princess-dressup/assets"
paths = [
    "player_fixed/front.png", 
    "player_fixed/back.png", 
    "player_fixed/side.png", 
    "dog_fixed/idle.png"
]

for p in paths:
    final_clean(os.path.join(DIR, p))

print("All individual assets cleaned perfectly!")
