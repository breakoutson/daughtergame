from PIL import Image
import os

def make_transparent(image_path):
    if not os.path.exists(image_path):
        return
    
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    # 배경을 투명하게 (흰색에 가까운 색들 제거)
    threshold = 240 
    for item in datas:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0)) # 투명하게
        else:
            new_data.append(item)

    img.putdata(new_data)
    # 덮어쓰기
    img.save(image_path, "PNG")
    print(f"Cleaned: {image_path}")

assets_dir = "/Users/son-yongseok/aidev/princess-dressup/assets"
files = ["character.png", "bunny.png", "chest.png", "pink_dress.png", "yellow_dress.png", "crown.png", "shoes.png", "wings.png"]

for file in files:
    make_transparent(os.path.join(assets_dir, file))
