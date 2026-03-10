import pygame
import sys
import os
import math
import random

# --- 1. 초기화 & 화면 설정 ---
pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("👸 우리 딸 공주님 어드벤처 V7 - ROBLOX Style 👸")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

def load_img(path, scale=None):
    fp = os.path.join(ASSETS, path)
    if not os.path.exists(fp): return None
    img = pygame.image.load(fp).convert_alpha()
    if scale:
        img = pygame.transform.smoothscale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    return img

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(500, 500)
        self.speed = 6
        self.direction = "front"
        self.moving = False
        self.outfit = {"dress": None, "wings": False, "acc": False}
        
        # 원본 소스 (깨짐 방지 위해 고해상도로 유지 및 참조)
        self.raw_images = {
            "front": load_img("player_v6/front.png"),
            "back": load_img("player_v6/back.png"),
            "side_l": load_img("player_v6/side_l.png"),
            "side_r": load_img("player_v6/side_r.png"),
        }
        # 집 안 캐릭터 기본 크기 (220px로 약간 상향)
        self.base_height = 220
        self.images = {}
        self._refresh_images(1.0)
        
        # 방향 교정: side_r을 기본으로 쓰고 side_l은 flip 처리
        self.raw_images["side_r"] = self.raw_images.get("side_r")
        if self.raw_images["side_r"]:
            self.raw_images["side_l"] = pygame.transform.flip(self.raw_images["side_r"], True, False)
        
        # 옷들도 미리 로드
        self.clothes = {
            "pink": load_img("pink_dress_fixed.png"),
            "yellow": load_img("yellow_dress_fixed.png"),
            "wings": load_img("wings_fixed.png"),
            "crown": load_img("crown_fixed.png")
        }

    def _refresh_images(self, sc):
        for k, v in self.raw_images.items():
            if v:
                h = int(self.base_height * sc)
                w = int(v.get_width() * (h / v.get_height()))
                self.images[k] = pygame.transform.smoothscale(v, (w, h))

    def update(self, keys, obstacles):
        dv = pygame.Vector2(0, 0)
        
        # 키 입력 (확실한 방향 감지)
        if keys[pygame.K_LEFT]: dv.x = -1; self.direction = "side_l"
        elif keys[pygame.K_RIGHT]: dv.x = 1; self.direction = "side_r"
        elif keys[pygame.K_UP]: dv.y = -1; self.direction = "back"
        elif keys[pygame.K_DOWN]: dv.y = 1; self.direction = "front"

        if dv.length() > 0:
            new_pos = self.pos + dv.normalize() * self.speed
            # 발 근처 작은 히트박스로 유연하게 이동
            char_rect = pygame.Rect(0, 0, 40, 20)
            char_rect.midbottom = (new_pos.x, new_pos.y)
            
            can_move = True
            for obs in obstacles:
                if char_rect.colliderect(obs):
                    can_move = False; break
            
            if can_move:
                self.pos = new_pos
            self.moving = True
        else:
            self.moving = False

        # 월드 경계
        self.pos.x = max(50, min(WIDTH-50, self.pos.x))
        self.pos.y = max(350, min(HEIGHT-10, self.pos.y))

    def draw(self, surf, center_at=None, zoom=1.0):
        at = center_at if center_at else self.pos
        img = self.images.get(self.direction)
        
        # 줌 처리 (고화질 유지)
        if zoom > 1.0:
            raw = self.raw_images.get(self.direction)
            if raw:
                h = int(self.base_height * zoom)
                w = int(raw.get_width() * (h / raw.get_height()))
                img = pygame.transform.smoothscale(raw, (w, h))
            
        if not img: return
        b = math.sin(pygame.time.get_ticks() * 0.015) * 4 if self.moving else 0
        rect = img.get_rect(center=(at.x, at.y + b))
        
        # 1. 날개 (캐릭터 뒤)
        if self.outfit["wings"]:
            w_img = self.clothes.get("wings")
            if w_img:
                wh = int(200 * zoom); ww = int(w_img.get_width() * (wh / w_img.get_height()))
                w_img_s = pygame.transform.smoothscale(w_img, (ww, wh))
                off_z = -5 if self.direction == "back" else 5
                surf.blit(w_img_s, w_img_s.get_rect(center=(at.x, at.y + off_z*zoom + b)))

        # 2. 캐릭터 본체 (내복이 포함된 베이스)
        surf.blit(img, rect)
        
        # 3. 옷 & 왕관 (모든 방향 적용)
        if self.outfit["dress"]:
            d_img_raw = self.clothes.get(self.outfit["dress"])
            if d_img_raw:
                dh = int(140 * zoom); dw = int(d_img_raw.get_width() * (dh / d_img_raw.get_height()))
                d_img = pygame.transform.smoothscale(d_img_raw, (dw, dh))
                
                # 방향에 따른 드레스 보정
                if self.direction == "side_l":
                    d_img = pygame.transform.flip(d_img, True, False) # 드레스도 플립
                    d_img = pygame.transform.smoothscale(d_img, (int(dw*0.6), dh)) # 옆모습은 좁게
                elif self.direction == "side_r":
                    d_img = pygame.transform.smoothscale(d_img, (int(dw*0.6), dh))
                elif self.direction == "back":
                    # 뒷모습은 드레스만 보이면 되므로 본체 위에 덮어씌움 (내복 가리기)
                    d_img = pygame.transform.smoothscale(d_img, (dw, dh))
                
                # 드레스 위치 (내복을 최대한 가리도록 살짝 위로 조정)
                off_y = 60 * zoom
                surf.blit(d_img, d_img.get_rect(center=(at.x, at.y + off_y + b)))
            
        if self.outfit["acc"]:
            a_img_raw = self.clothes.get("crown")
            if a_img_raw:
                ah = int(50 * zoom); aw = int(a_img_raw.get_width() * (ah / a_img_raw.get_height()))
                a_img = pygame.transform.smoothscale(a_img_raw, (aw, ah))
                if self.direction == "side_l": a_img = pygame.transform.flip(a_img, True, False)
                
                off_y = -95 * zoom
                surf.blit(a_img, a_img.get_rect(center=(at.x, at.y + off_y + b)))

class Dog:
    def __init__(self):
        # 강아지 사이즈 상향 (0.3 -> 0.6)
        sc = 0.6
        self.images = {
            "idle": load_img("dog_v6/idle.png", sc),
            "walk_1": load_img("dog_v6/walk_1.png", sc),
            "walk_2": load_img("dog_v6/walk_2.png", sc),
            "sleep": load_img("dog_v6/sleep.png", sc),
        }
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
        # 캐릭터 시작 위치 조정 (장애물 밖으로)
        self.player.pos = pygame.Vector2(500, 650)
        self.dog = Dog()
        self.room = "living"
        self.bgs = {
            "living": load_img("rooms/living_roblox.png"),
            "wardrobe": load_img("rooms/wardrobe_roblox.png"),
            "bedroom": load_img("rooms/bedroom_roblox.png")
        }
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        # 장애물 히트박스 최적화 (이동 공간 확보)
        self.obstacles = [
            pygame.Rect(60, 520, 350, 100),  # 소파
            pygame.Rect(440, 430, 140, 70),  # 벽난로
            pygame.Rect(440, 670, 250, 40),  # 테이블
            pygame.Rect(720, 520, 250, 150), # 창가 수납장
        ]
        # 문 영역 (거절되지 않을 정도의 넉넉한 히트박스)
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
                if event.type == pygame.MOUSEBUTTONDOWN: click = True

            bg = self.bgs.get(self.room)
            if bg: screen.blit(pygame.transform.scale(bg, (WIDTH, HEIGHT)), (0, 0))

            if self.room == "living":
                self.player.update(keys, self.obstacles)
                self.dog.update(self.obstacles)
                self.player.draw(screen)
                self.dog.draw(screen)
                
                # 방 이동 가이드
                screen.blit(self.font.render("Dress Room ->", True, (0, 0, 0)), (850, 450))
                
                for target, rect in self.doors.items():
                    if rect.collidepoint(self.player.pos):
                        self.room = target
                        self.player.direction = "front" # 방 진입 시 정면 응시
                        self.player.pos = pygame.Vector2(WIDTH//2, 650)
            else:
                # 옷방 전문 (캐릭터 2.5배 확대, 픽셀 깨짐 방지 처리됨)
                self.player.draw(screen, center_at=pygame.Vector2(WIDTH//2, HEIGHT//2), zoom=2.5)
                
                # EXIT
                exit_r = pygame.Rect(WIDTH-150, 40, 120, 50)
                pygame.draw.rect(screen, (255, 100, 100), exit_r, border_radius=15)
                screen.blit(self.font.render("<- EXIT", True, (255, 255, 255)), (WIDTH-130, 52))
                if click and exit_r.collidepoint(mx, my):
                    self.room = "living"; self.player.pos = pygame.Vector2(800, 500)

                # 옷 입히기 UI (토글 완벽 구현)
                if self.room == "wardrobe":
                    pygame.draw.rect(screen, (255, 255, 255, 210), (0, 600, WIDTH, 150))
                    items = [
                        ("pink", (150, 620), "dress"),
                        ("yellow", (350, 620), "dress"),
                        ("wings", (580, 620), "wings"),
                        ("crown", (810, 620), "acc")
                    ]
                    for key, pos, cat in items:
                        icon_raw = self.player.clothes.get(key if cat != "acc" else "crown")
                        icon = pygame.transform.scale(icon_raw, (100, 100))
                        btn = pygame.Rect(pos[0], pos[1], 100, 100)
                        
                        # 장착 강조
                        is_on = (cat == "dress" and self.player.outfit["dress"] == key) or \
                                (cat == "wings" and self.player.outfit["wings"]) or \
                                (cat == "acc" and self.player.outfit["acc"])
                        if is_on: pygame.draw.rect(screen, (255, 215, 0), btn.inflate(10, 10), 4)

                        screen.blit(icon, pos)
                        if click and btn.collidepoint(mx, my):
                            if cat == "dress":
                                self.player.outfit["dress"] = None if self.player.outfit["dress"] == key else key
                            elif cat == "wings": self.player.outfit["wings"] = not self.player.outfit["wings"]
                            elif cat == "acc": self.player.outfit["acc"] = not self.player.outfit["acc"]

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__": GameEngine().run()
