import pygame
import sys
import os
import math
import random
import json

# --- 1. 초기화 & 화면 설정 ---
pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("👸 우리 딸 공주님 어드벤처 V10 - 퍼펙트 핏 코디 시스템 👸")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")
V10_ASSETS = os.path.join(ASSETS, "v10_items")
V10_PLAYER = os.path.join(ASSETS, "player_v10") # 반팔/반바지 처리된 V6 베이스 (유저가 좋아하던 그림체 유지)

def load_img(path, scale=None):
    if not os.path.exists(path): return None
    img = pygame.image.load(path).convert_alpha()
    return img

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(500, 500)
        self.speed = 6
        self.direction = "front"
        self.moving = False
        
        # V10 의상 카탈로그 로드
        with open(os.path.join(V10_ASSETS, "catalog.json"), "r") as f:
            self.catalog = json.load(f)
            
        self.outfit = {k: None for k in self.catalog.keys()}
        
        self.item_images = {}
        for cat, items in self.catalog.items():
            for item in items: 
                self.item_images[item["file"]] = {
                    "img": load_img(os.path.join(V10_ASSETS, item["file"])),
                    "type": item.get("type", "top")
                }

        # 베이스 캐릭터 (크롬 등 브라우저 지원용 고화질 유지)
        self.base_height = 220
        self.raw_images = {
            "front": load_img(os.path.join(V10_PLAYER, "front.png")),
            "back": load_img(os.path.join(V10_PLAYER, "back.png")),
            "side_l": load_img(os.path.join(V10_PLAYER, "side_l.png")),
            "side_r": load_img(os.path.join(V10_PLAYER, "side_r.png")),
        }
        
        # 캐릭터 비율 매칭표 (V6 베이스 사이즈: 143x285 픽셀 비율 기준)
        self.fit_config = {
            "hair": {"width_ratio": 0.95, "y_anchor": 0.22, "align": "center"}, # 머리 전체
            "hat": {"width_ratio": 0.80, "y_anchor": 0.15, "align": "midbottom"}, # 머리 위
            "glasses": {"width_ratio": 0.45, "y_anchor": 0.35, "align": "center"}, 
            "sunglasses": {"width_ratio": 0.45, "y_anchor": 0.35, "align": "center"},
            "top": {"width_ratio": 0.60, "y_anchor": 0.47, "align": "midtop"}, # 목 아래
            "bottom": {"width_ratio": 0.58, "y_anchor": 0.61, "align": "midtop"}, # 허리 아래
            "pajamas": {"width_ratio": 0.65, "y_anchor": 0.47, "align": "midtop"}, 
            "tracksuit": {"width_ratio": 0.65, "y_anchor": 0.47, "align": "midtop"},
            "party_dress": {"width_ratio": 0.85, "y_anchor": 0.47, "align": "midtop"}, 
            "shoes_sneakers": {"width_ratio": 0.45, "y_anchor": 0.96, "align": "midbottom"}, 
            "shoes_slippers": {"width_ratio": 0.45, "y_anchor": 0.96, "align": "midbottom"},
            "shoes_dress": {"width_ratio": 0.45, "y_anchor": 0.96, "align": "midbottom"},
            "bag": {"width_ratio": 0.35, "y_anchor": 0.65, "align": "center"}
        }

    def update(self, keys, obstacles):
        dv = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]: dv.x = -1; self.direction = "side_l"
        elif keys[pygame.K_RIGHT]: dv.x = 1; self.direction = "side_r"
        elif keys[pygame.K_UP]: dv.y = -1; self.direction = "back"
        elif keys[pygame.K_DOWN]: dv.y = 1; self.direction = "front"

        if dv.length() > 0:
            new_pos = self.pos + dv.normalize() * self.speed
            char_rect = pygame.Rect(0, 0, 40, 20)
            char_rect.midbottom = (new_pos.x, new_pos.y)
            can_move = True
            for obs in obstacles:
                if char_rect.colliderect(obs):
                    can_move = False; break
            if can_move: self.pos = new_pos
            self.moving = True
        else:
            self.moving = False

        self.pos.x = max(50, min(WIDTH-50, self.pos.x))
        self.pos.y = max(350, min(HEIGHT-10, self.pos.y))

    def draw_item(self, surf, item_obj, cat, rect_base, zoom, b):
        file_name = item_obj["file"]
        data = self.item_images.get(file_name)
        if not data or not data["img"]: return
        
        img_raw = data["img"]
        cfg = self.fit_config.get(cat, {"width_ratio": 0.5, "y_anchor": 0.5, "align": "center"})
        
        target_w = int(rect_base.width * cfg["width_ratio"])
        target_h = int(img_raw.get_height() * (target_w / img_raw.get_width()))
        
        off_x = 0
        img = img_raw
        if self.direction == "side_l":
             img = pygame.transform.flip(img_raw, True, False)
             target_w = int(target_w * 0.7)
             off_x = -15 * zoom
        elif self.direction == "side_r":
             target_w = int(target_w * 0.7)
             off_x = 15 * zoom
        elif self.direction == "back":
             if cat in ["glasses", "sunglasses", "bag", "hat"]: return
             
        if cat == "bag":
            off_x = (-45 * zoom) if self.direction in ["front", "side_l"] else (45 * zoom)
             
        img = pygame.transform.smoothscale(img, (target_w, target_h))
        img_rect = img.get_rect()
        
        anchor_y = rect_base.top + (rect_base.height * cfg["y_anchor"])
        
        # 정밀 정렬 알고리즘 적용
        if cfg["align"] == "midtop":
            img_rect.midtop = (rect_base.centerx + off_x, anchor_y + b)
        elif cfg["align"] == "midbottom":
            img_rect.midbottom = (rect_base.centerx + off_x, anchor_y + b)
        else:
            img_rect.center = (rect_base.centerx + off_x, anchor_y + b)
            
        surf.blit(img, img_rect)

    def draw(self, surf, center_at=None, zoom=1.0):
        at = center_at if center_at else self.pos
        raw = self.raw_images.get(self.direction)
        if not raw: return
        
        h = int(self.base_height * zoom)
        w = int(raw.get_width() * (h / raw.get_height()))
        img = pygame.transform.smoothscale(raw, (w, h))
        
        b = math.sin(pygame.time.get_ticks() * 0.015) * 4 if self.moving else 0
        
        char_rect = img.get_rect(center=(at.x, at.y + b))
        surf.blit(img, char_rect)

        # 의상 레이어 그리기
        draw_order = [
            "bottom", "top", "pajamas", "tracksuit", "party_dress", 
            "shoes_sneakers", "shoes_slippers", "shoes_dress",
            "hair", "glasses", "sunglasses", "bag", "hat"
        ]
        
        for cat in draw_order:
            item_obj = self.outfit.get(cat)
            if item_obj:
                self.draw_item(surf, item_obj, cat, char_rect, zoom, b)

class Dog:
    def __init__(self):
        sc = 0.6
        self.images = {
            "idle": load_img(os.path.join(ASSETS, "dog_v6/idle.png")),
            "walk_1": load_img(os.path.join(ASSETS, "dog_v6/walk_1.png")),
            "walk_2": load_img(os.path.join(ASSETS, "dog_v6/walk_2.png")),
            "sleep": load_img(os.path.join(ASSETS, "dog_v6/sleep.png")),
        }
        for k, v in self.images.items():
            if v:
                self.images[k] = pygame.transform.smoothscale(v, (int(v.get_width()*sc), int(v.get_height()*sc)))

        self.pos = pygame.Vector2(300, 600)
        self.state = "idle"
        self.target = pygame.Vector2(self.pos)
        self.timer = 0

    def update(self, obstacles):
        self.timer += 1
        if self.timer % 150 == 0:
            self.state = random.choice(["idle", "walk", "sleep"])
            if self.state == "walk":
                self.target = pygame.Vector2(random.randint(100, 900), random.randint(400, 700))

        if self.state == "walk":
            dist = self.target - self.pos
            if dist.length() > 5:
                self.pos += dist.normalize() * 1.2
            else: self.state = "idle"
            
    def draw(self, surf):
        img_key = self.state if self.state != "walk" else ("walk_1" if (pygame.time.get_ticks()//200)%2 == 0 else "walk_2")
        img = self.images.get(img_key)
        if img: surf.blit(img, img.get_rect(center=self.pos))

class GameEngine:
    def __init__(self):
        self.player = Player()
        self.player.pos = pygame.Vector2(500, 650)
        self.dog = Dog()
        self.room = "living"
        self.bgs = {
            "living": load_img(os.path.join(ASSETS, "rooms/living_roblox.png")),
            "wardrobe": load_img(os.path.join(ASSETS, "rooms/wardrobe_roblox.png")),
            "bedroom": load_img(os.path.join(ASSETS, "rooms/bedroom_roblox.png"))
        }
        if self.bgs["living"]: self.bgs["living"] = pygame.transform.scale(self.bgs["living"], (WIDTH, HEIGHT))
        if self.bgs["wardrobe"]: self.bgs["wardrobe"] = pygame.transform.scale(self.bgs["wardrobe"], (WIDTH, HEIGHT))
        if self.bgs["bedroom"]: self.bgs["bedroom"] = pygame.transform.scale(self.bgs["bedroom"], (WIDTH, HEIGHT))

        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.cat_font = pygame.font.SysFont("arial", 26, bold=True)
        
        self.category_names = list(self.player.catalog.keys())
        self.current_cat_idx = 0
        
        self.obstacles = [
            pygame.Rect(60, 520, 350, 100),
            pygame.Rect(440, 430, 140, 70),
            pygame.Rect(440, 670, 250, 40),
            pygame.Rect(720, 520, 250, 150),
        ]
        self.doors = {
            "wardrobe": pygame.Rect(900, 400, 100, 300),
            "bedroom": pygame.Rect(350, 350, 300, 80)
        }

    def run(self):
        while True:
            screen.fill((255, 255, 255))
            keys = pygame.key.get_pressed()
            mx, my = pygame.mouse.get_pos()
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: click = True

            bg = self.bgs.get(self.room)
            if bg: screen.blit(bg, (0, 0))

            ui_rect = pygame.Rect(0, 500, WIDTH, 250)

            if self.room == "living":
                self.player.update(keys, self.obstacles)
                self.dog.update(self.obstacles)
                self.player.draw(screen)
                self.dog.draw(screen)
                
                screen.blit(self.font.render("Dress Room ->", True, (0, 0, 0)), (850, 450))
                for target, rect in self.doors.items():
                    if rect.collidepoint(self.player.pos):
                        self.room = target
                        self.player.direction = "front"
                        self.player.pos = pygame.Vector2(WIDTH//2, 600)
            else:
                # 얼굴/발 안잘리게 적당한 스케일과 위치
                self.player.draw(screen, center_at=pygame.Vector2(WIDTH//2, 250), zoom=1.7)
                
                exit_r = pygame.Rect(WIDTH-150, 40, 120, 50)
                pygame.draw.rect(screen, (255, 100, 100), exit_r, border_radius=15)
                screen.blit(self.font.render("<- EXIT", True, (255, 255, 255)), (WIDTH-130, 52))
                if click and exit_r.collidepoint(mx, my):
                    self.room = "living"; self.player.pos = pygame.Vector2(800, 500)

                if self.room == "wardrobe":
                    pygame.draw.rect(screen, (255, 255, 255, 230), ui_rect)
                    
                    cat_name = self.category_names[self.current_cat_idx]
                    prev_btn = pygame.Rect(50, 510, 50, 40)
                    next_btn = pygame.Rect(WIDTH-100, 510, 50, 40)
                    pygame.draw.rect(screen, (200, 200, 200), prev_btn, border_radius=5)
                    pygame.draw.rect(screen, (200, 200, 200), next_btn, border_radius=5)
                    screen.blit(self.font.render("<", True, (0,0,0)), (65, 520))
                    screen.blit(self.font.render(">", True, (0,0,0)), (WIDTH-85, 520))
                    
                    label = self.cat_font.render(f"--- {cat_name.upper()} ---", True, (50, 50, 50))
                    screen.blit(label, (WIDTH//2 - label.get_width()//2, 515))
                    
                    if click:
                        if prev_btn.collidepoint(mx, my): self.current_cat_idx = (self.current_cat_idx - 1) % len(self.category_names)
                        if next_btn.collidepoint(mx, my): self.current_cat_idx = (self.current_cat_idx + 1) % len(self.category_names)

                    items = self.player.catalog.get(cat_name, [])
                    start_x = 50
                    y = 570
                    
                    for idx, item in enumerate(items):
                        if idx >= 10: break
                        icon_x = start_x + (idx * 90)
                        btn = pygame.Rect(icon_x, y, 80, 80)
                        pygame.draw.rect(screen, (240, 240, 240), btn, border_radius=10)
                        
                        if self.player.outfit[cat_name] == item:
                            pygame.draw.rect(screen, (255, 200, 0), btn.inflate(8,8), 4, border_radius=10)
                            
                        raw_data = self.player.item_images.get(item["file"])
                        if raw_data and raw_data["img"]:
                            raw_img = raw_data["img"]
                            thumb = pygame.transform.smoothscale(raw_img, (60, int(60 * raw_img.get_height()/raw_img.get_width())))
                            screen.blit(thumb, thumb.get_rect(center=btn.center))
                            
                        if click and btn.collidepoint(mx, my):
                            # 호환성 리셋
                            if cat_name in ["pajamas", "tracksuit", "party_dress"]:
                                self.player.outfit["top"] = None; self.player.outfit["bottom"] = None
                            if cat_name in ["top", "bottom"]:
                                self.player.outfit["pajamas"] = None; self.player.outfit["tracksuit"] = None; self.player.outfit["party_dress"] = None
                            if cat_name.startswith("shoes_"):
                                self.player.outfit["shoes_sneakers"] = None
                                self.player.outfit["shoes_slippers"] = None
                                self.player.outfit["shoes_dress"] = None
                                
                            self.player.outfit[cat_name] = None if self.player.outfit[cat_name] == item else item

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__": GameEngine().run()
