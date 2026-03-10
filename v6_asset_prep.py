from PIL import Image, ImageDraw
import os

def clean_and_save(img, name, output_dir):
    # 1. 완벽 배경 제거 (Floodfill)
    img = img.convert("RGBA")
    for seed in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)]:
        ImageDraw.floodfill(img, seed, (0, 0, 0, 0), thresh=50)
    
    # 2. 타이트 크롭
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    
    img.save(os.path.join(output_dir, f"{name}.png"))

def prepare_v6_assets():
    ASSETS = "/Users/son-yongseok/aidev/princess-dressup/assets"
    BRAIN = "/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3"
    
    char_sheet_path = os.path.join(BRAIN, "chibi_base_pajamas_parts_1773148226466.png")
    dog_sheet_path = os.path.join(BRAIN, "maltese_moving_parts_1773148241643.png")

    char_dir = os.path.join(ASSETS, "player_v6")
    dog_dir = os.path.join(ASSETS, "dog_v6")
    os.makedirs(char_dir, exist_ok=True)
    os.makedirs(dog_dir, exist_ok=True)

    # 1. 캐릭터 슬라이싱 (1024x1024 sheet, 4 parts)
    char_sheet = Image.open(char_sheet_path)
    w, h = char_sheet.size
    half_w, half_h = w // 2, h // 2
    
    clean_and_save(char_sheet.crop((0, 0, half_w, half_h)), "front", char_dir)
    clean_and_save(char_sheet.crop((half_w, 0, w, half_h)), "back", char_dir)
    clean_and_save(char_sheet.crop((0, half_h, half_w, h)), "side_l", char_dir)
    clean_and_save(char_sheet.crop((half_w, half_h, w, h)), "side_r", char_dir)

    # 2. 강아지 슬라이싱 (4 horizontal parts)
    dog_sheet = Image.open(dog_sheet_path)
    dw, dh = dog_sheet.size
    part_w = dw // 4
    
    clean_and_save(dog_sheet.crop((0, 0, part_w, dh)), "idle", dog_dir)
    clean_and_save(dog_sheet.crop((part_w, 0, 2*part_w, dh)), "walk_1", dog_dir)
    clean_and_save(dog_sheet.crop((2*part_w, 0, 3*part_w, dh)), "walk_2", dog_dir)
    clean_and_save(dog_sheet.crop((3*part_w, 0, dw, dh)), "sleep", dog_dir)

    print("V6 Assets Ready!")

prepare_v6_assets()
